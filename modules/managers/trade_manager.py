"""Trade Module."""

from datetime import date
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, model_validator

from models.account.account import Account
from models.input.input import TradeRuleSettings
from models.rules.rules import TradeRule
from models.rules.execution import ExecutionRule, TradeMessageModel, Trades
from models.trades.schedule import TradeSchedule

if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel


class TradeManager(BaseModel):
    """Trade Manager Model."""

    trade_rule_settings: List[TradeRuleSettings]
    backtester_trades: Optional[TradeSchedule] = None

    @model_validator(mode="after")
    def post_validate_model(self):
        if not self.backtester_trades:
            self.backtester_trades = TradeSchedule(trades=[])
        return self

    def execute_trades(self, current_date: date, data: "MarketModel", account: Account):
        """Execute trades."""
        self._manage_open_trades(data=data, date=current_date, account=account)
        self._evaluate_new_trades(data=data, date=current_date, account=account)

    def _manage_open_trades(self, data: "MarketModel", date: date, account: Account):
        """Manage open trades."""
        live_trades = self.backtester_trades.get_live_trades()
        for trade in live_trades:
            signal = self._evaluate_close_signals(data=data, date=date, trade=trade)
            if signal:
                self.close_trade(
                    date=date, data=data, trade=trade, signal=signal, account=account
                )

    def _evaluate_new_trades(self, data: "MarketModel", date: date, account: Account):
        """Evaluate new trade positions."""
        for trade_rule_setting in self.trade_rule_settings:
            for trade_execution_rule in trade_rule_setting.execution_rules:
                for signal in trade_rule_setting.open_rules:
                    if signal.evaluate(
                        snapshot=data,
                        date=date,
                        trade=trade_execution_rule.trades[0],  # unsure about this
                        trade_schedule=self.backtester_trades,
                    ):
                        self.open_trade(
                            data=data,
                            date=date,
                            trade_rule=signal,
                            trade_execution_rule=trade_execution_rule,
                            account=account,
                        )

    def _evaluate_close_signals(
        self, data: "MarketModel", date: date, trade: Trades
    ) -> TradeRule | bool:
        """Evaluate close signals."""
        open_trade_rule = trade.message[0].trade_rule
        relevant_rule = next(
            trade_rule_setting
            for trade_rule_setting in self.trade_rule_settings
            if trade_rule_setting.open_rules == [open_trade_rule]
        )
        for signal in (
            relevant_rule.close_rules
            + relevant_rule.stoploss_rules
            + relevant_rule.takeprofit_rules
        ):
            if signal.evaluate(
                snapshot=data,
                date=date,
                trade=trade,
                trade_schedule=self.backtester_trades,
            ):
                return signal
        return False

    def open_trade(
        self,
        data: "MarketModel",
        date: date,
        trade_rule: TradeRule,
        trade_execution_rule: ExecutionRule,
        account: Account,
    ):
        """Open trade and append to trade schedule."""
        self.backtester_trades.trades.extend(
            trade_execution_rule.execute(
                trade_rule=trade_rule, data=data, date=date, account=account
            )
        )

    def close_trade(
        self,
        date: date,
        data: "MarketModel",
        trade: Trades,
        signal: TradeRule,
        account: Account,
    ):
        """Close trade."""
        trade.value_date = date
        trade.close_price = data.get(
            market_variable="Spot",
            underlying=trade.underlying,
            date=date,
            asset_class=trade.asset_class,
        )
        account.update_balance_for_close_trade(trade=trade)
        trade.message.append(TradeMessageModel(date=date, message=signal.rule_type))
