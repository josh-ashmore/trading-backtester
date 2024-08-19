"""Backtester Input Models."""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, model_validator

from models.account.account import Account
from models.configs.config_models import Configs
from models.input.market_data_settings import MarketDataSettings, SignalDataModel
from models.input.trade_data_settings import TradeDataSettings
from models.input.trade_rule_settings import TradeRuleSettings
from models.market_data.market_model import MarketModel


class BaseStrategyInput(BaseModel):
    """Top Level Base Strategy Input Model."""

    data: MarketModel
    market_data_settings: MarketDataSettings
    trade_data_settings: TradeDataSettings
    trade_rule_settings: List[TradeRuleSettings]
    configs: List[Configs] = []

    account: Account
    signal_data: Optional[List[SignalDataModel]] = None

    dates: Optional[List[date]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        self._prepare_account()
        self._prepare_base_trade()
        self._prepare_dates()
        return self

    def _prepare_account(self):
        """Prepare account if not provided."""
        if not self.account:
            self.account = Account(
                currency=self.market_data_settings.currency,
                initial_balance=500,
                current_balance=500,
            )

    def _prepare_base_trade(self):
        """Prepare base trade."""
        self.trade_data_settings.base_trade = self.trade_data_settings.base_trade | {
            "notional_currency": self.account.currency,
            "underlying": self.market_data_settings.underlying,
            "premium_currency": self.account.currency,
            "strike_style": "ATM EXPIRY",
            "asset_class": self.market_data_settings.asset_class,
        }

    def _prepare_dates(self):
        """Prepare dates for backtester module."""
        if not self.dates:
            self.dates = [
                datum.spot_date
                for datum in getattr(self.data, self.market_data_settings.asset_class)[
                    self.market_data_settings.underlying
                ].spot
            ]
        if isinstance(self.dates[0], set):
            self.dates = self.dates[0]
        self.dates = sorted(self.dates)

    def get_trades_to_execute(self):
        """Get trades to execute from trade details."""
        trades_to_execute = []
        for trade_rule_setting in self.trade_rule_settings:
            for execution_rule in trade_rule_setting.execution_rules:
                trades_to_execute.append(execution_rule.trades)
        return trades_to_execute
