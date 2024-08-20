"""Backtester Models."""

from datetime import date
from typing import TYPE_CHECKING, Any, Optional
from pydantic import BaseModel, ConfigDict, model_validator

from models.input.input import BaseStrategyInput
from models.output.output import BacktesterOutput

from models.trades.schedule import TradeSchedule
from models.trades.spot_trade import EQSpotTrade, FXSpotTrade, Trades

if TYPE_CHECKING:
    from models.rules.rules import TradeRule


class Backtester(BaseModel):
    """Main Backtester Module.


    Handles all logic for running a backtest
    given user input.
    """

    strategy_input: BaseStrategyInput

    strategy_output: Optional[BacktesterOutput] = None
    trades: Optional[TradeSchedule] = None

    STYLE_DICT: dict[str, Any] = {
        "FXSpotTrade": FXSpotTrade,
        "EQSpotTrade": EQSpotTrade,
    }

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if not self.strategy_output:
            self.strategy_output = BacktesterOutput()
        if not self.trades:
            self.trades = TradeSchedule(trades=[])
        return self

    def _check_signal_triggered(self, date: date):
        """Check if signal is triggered."""
        live_trades = [trade for trade in self.trades.trades if trade.open]
        for _trade in live_trades:
            self._is_stoploss_triggered(trade=_trade, date=date)
            self._is_close_triggered(trade=_trade, date=date)
        self._is_open_triggered(date=date)

    def _is_open_triggered(self, date: date):
        """Open signal triggered."""
        if self.strategy_input.trade_rule_settings.open_rules:
            for rule in self.strategy_input.trade_rule_settings.open_rules:
                for trade_exection in rule.execution:
                    for trade_details in trade_exection.trade_details:
                        trade_dict = self.strategy_input.trade_data_settings.base_trade
                        # calculate value_date
                        value_date = min(
                            (
                                _date
                                for _date in set(
                                    self.strategy_input.snapshot.market_model.eq_vols[
                                        date
                                    ]["GLD"].expiry_dates
                                )
                                if _date >= date
                            ),
                            key=lambda x: (x - date),
                        )
                        trade = self.STYLE_DICT[trade_details.style](
                            **{
                                **trade_dict,
                                **trade_details.model_dump(),
                                **{
                                    "trade_date": date,
                                    "value_date": value_date,
                                    "premium_payment_date": date,
                                },
                            }
                        )
                        if rule.evaluate(
                            trade=trade,
                            snapshot=self.strategy_input.snapshot,
                            date=date,
                        ):
                            self._execute_trade(trade=trade, date=date, rule=rule)
                            # return

    def _is_close_triggered(self, trade: Trades, date: date):
        """Close signal triggered."""
        if self.strategy_input.trade_rule_settings.close_rules and trade.open:
            for rule in self.strategy_input.trade_rule_settings.close_rules:
                if rule.evaluate(
                    trade=trade, snapshot=self.strategy_input.snapshot, date=date
                ):
                    self._execute_trade(trade=trade, date=date, rule=rule)
                    return

    def _is_stoploss_triggered(self, trade: Trades, date: date):
        """Stoploss signal triggered."""
        if self.strategy_input.trade_rule_settings.stoploss_rules and trade.open:
            for rule in self.strategy_input.trade_rule_settings.stoploss_rules:
                if rule.evaluate(
                    trade=trade, snapshot=self.strategy_input.snapshot, date=date
                ):
                    self._execute_trade(trade=trade, date=date, rule=rule)
                    return

    def _is_takeprofit_triggered(self, trade: Trades, date: date):
        """Take profit signal triggered."""
        if self.strategy_input.trade_rule_settings.takeprofit_rules and trade.open:
            for rule in self.strategy_input.trade_rule_settings.takeprofit_rules:
                if rule.evaluate(
                    trade=trade, snapshot=self.strategy_input.snapshot, date=date
                ):
                    self._execute_trade(trade=trade, date=date, rule=rule)
                    return

    def _execute_trade(self, trade: Trades, date: date, rule: "TradeRule"):
        """Execute (open/close) trade.


        - Append trade to trades.
        - Update account to reflect cost.
        """
        for trade_execution in rule.execution:
            trade_execution.validate_required_signals(
                snapshot=self.strategy_input.snapshot
            )
            for trade_details in trade_execution.trade_details:
                notional_amount = trade_execution.calculate_notional(
                    trade=trade_details,
                    date=date,
                    snapshot=self.strategy_input.snapshot,
                    account=self.strategy_input.account,
                )
                base_trade = self.strategy_input.trade_data_settings.base_trade

                new_trade: Trades = self.STYLE_DICT[trade_details.style](
                    **base_trade,
                    **trade_details.execute_trade(
                        snapshot=self.strategy_input.snapshot
                    ),
                    notional_amount=notional_amount,
                )

                # unsure if need to iterate over both or only first leg
                for leg in new_trade:
                    trade_execution.slippage_adjustment(
                        trade=new_trade,
                        leg=leg,
                        account_slippage_=True,
                        notional_adjustment=False,
                    )

                self.strategy_input.market_data_settings.pricing_model.bind_trades(
                    [new_trade]
                )
                new_trade.adjust_trade(data=self.strategy_input.snapshot)

                self.trades.trades.append(new_trade)
                self._update_account(trade=new_trade)

    def _update_account(self, trade: Trades):
        """Update account."""
        for leg in trade.legs:
            self.strategy_input.account.access(
                data=self.strategy_input.snapshot,
                notional=leg.premium,
                ccy=self.strategy_input.trade_data_settings.base_trade[
                    "premium_currency"
                ],
                date=leg.trade_date,
                for_ccy=True,
            )

    def _adjust_account(self):
        """Adjust account.


        - Increase by cash amount (cash adjustment)
        """

    def _calculate_daily_statistics(self, date: date):
        """Calculate daily statistics."""
        settlement = sum(
            [
                _t.settlement(
                    data=self.strategy_input.snapshot,
                    ccy=self.strategy_input.trade_data_settings.base_trade[
                        "premium_currency"
                    ],
                    sorted_snapshot_dates=sorted(
                        self.strategy_input.snapshot.snapshot_dates
                    ),
                )
                for _t in self.trades.trades
                if _t.trade_date == date
            ]
        )[0][0]
        self.strategy_input.account.access(
            data=self.strategy_input.snapshot,
            notional=settlement,
            ccy=self.strategy_input.trade_data_settings.base_trade["premium_currency"],
            date=date,
            for_ccy=True,
        )
        self.strategy_output.live_pnl += settlement

    def run(self) -> BacktesterOutput:
        """Run backtester module."""
        self.strategy_input.account.reset()
        for _date in self.strategy_input.dates:
            self._check_signal_triggered(date=_date)
            self._adjust_account()
            self._calculate_daily_statistics(date=_date)

        return self.strategy_output._calculate(
            snapshot=self.strategy_input.snapshot,
            dates=self.strategy_input.dates,
            trades=self.trades,
            output_currency=None,
        )
