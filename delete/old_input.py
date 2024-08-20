"""Backtester Input Models."""

from contextlib import suppress
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, List, Optional
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.account.account import Account
from models.configs.config_models import Configs
from models.rules.enums import ActionType
from static_data.underlying_data import Currencies, StrategyAssetClasses
from models.rules.rules import TradeRule


if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel
    from models.rules.execution import ExecutionRule


class SignalDataModel(BaseModel):
    """Signal Data Model."""

    signal_name: str
    data: list[dict] | pd.DataFrame
    date_key_name: str
    value_key_name: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if not isinstance(self.data, pd.DataFrame):
            self.data = pd.DataFrame(data=self.data)
        return self

    def prepare_signal_data(self, market_data_set_dict: dict[date, Any]):
        """Prepare signal data to be ingested by pricing model."""
        data = self.data[[self.date_key_name, self.value_key_name]].dropna()
        dates = [
            _date
            for _date in data[self.date_key_name].apply(
                lambda x: datetime.strptime(x, "%Y-%m-%d").date()
            )
        ]
        data = dict(zip(dates, data[self.value_key_name]))
        data = {
            date_: data[date_] for date_ in data if date_ in market_data_set_dict.keys()
        }
        return data


class MarketDataSettings(BaseModel):
    """Market Data Settings."""

    spot_date: date
    underlying: str
    currency: Currencies = Field(examples=["USD"])
    pricing_currencies_map: dict[str, str] = Field(examples=[{"USD": "USD OIS"}])
    asset_class: StrategyAssetClasses = Field(examples=["FX", "EQ"])
    signal_data: Optional[list[SignalDataModel]] = None

    # pricing_model: Optional["MarketModel"] = (
    #     None  # should be an actual pricing model maybe?
    # )
    underlying_map: Optional[dict[str, str]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        self._set_pricing_model()
        self._set_underlying_map()
        return self

    def _set_pricing_model(self):
        """Set pricing model given asset class."""
        # asset_class = self.asset_class
        # match asset_class:
        #     case "FX":
        #         pricing_model = FXPricingModel
        #     case "EQ":
        #         pricing_model = EQPricingModel
        #     case _:
        #         raise NotImplementedError(
        #             f"Asset class: {asset_class} not yet implemented."
        #         )
        # self.pricing_model = pricing_model

    def _set_underlying_map(self):
        """Set underlying map."""
        self.underlying_map = {
            f"{self.asset_class.lower()}_underlyings": [self.underlying],
        }


class TradeDataSettings(BaseModel):
    """Trade Data Settings Model."""

    base_trade: Optional[dict[str, Any]] = None

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if not self.base_trade:
            self.base_trade = {
                "trade_date": None,
                "value_date": None,
                "delivery_date": None,
                "premium_payment_date": None,
                "moneyness": 1,
                "direction": "Sell",
                "historical": False,
                "dummy_curve": True,
                "premium": 0,
                "Restrike": False,  # would like to rename to lower
            }
        return self


class TradeRuleSettings(BaseModel):
    """Trade Rule Settings.

    Need to define this better.
    """

    trade_rules: list["TradeRule"]
    execution_rules: List["ExecutionRule"]

    open_rules: list["TradeRule"] | None = None
    close_rules: list["TradeRule"] | None = None
    stoploss_rules: list["TradeRule"] | None = None
    takeprofit_rules: list["TradeRule"] | None = None

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if self.open_rules is None:
            self.open_rules = [
                rule for rule in self.trade_rules if rule.rule_type == ActionType.OPEN
            ]
        if self.close_rules is None:
            self.close_rules = [
                rule for rule in self.trade_rules if rule.rule_type == ActionType.CLOSE
            ]
        if self.stoploss_rules is None:
            self.stoploss_rules = [
                rule
                for rule in self.trade_rules
                if rule.rule_type == ActionType.STOPLOSS
            ]
        if self.takeprofit_rules is None:
            self.takeprofit_rules = [
                rule
                for rule in self.trade_rules
                if rule.rule_type == ActionType.TAKE_PROFIT
            ]
        return self


class BaseStrategyInput(BaseModel):
    """Top Level Base Strategy Input Model."""

    data: "MarketModel"
    market_data_settings: MarketDataSettings
    trade_data_settings: TradeDataSettings
    trade_rule_settings: List[TradeRuleSettings]
    configs: List[Configs] = []

    account: Account
    signal_data: Optional[List[SignalDataModel]] = None

    snapshot: Optional["MarketModel"] = None
    dates: Optional[List[date]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        self._prepare_account()
        self._prepare_base_trade()
        self._prepare_pricing_model()
        if self.signal_data:
            self._prepare_signal_data()
        self._create_market_snapshot()
        self._prepare_dates()
        # Should have some logic around the configs - e.g.
        # adding new data for items like moving averages etc.
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
            # "notional_amounts": self.account.initial_balance,
            "underlying": self.market_data_settings.underlying,
            "premium_currency": self.account.currency,
            "strike_style": "ATM EXPIRY",
            "asset_class": self.market_data_settings.asset_class,
        }

    def _prepare_pricing_model(self):
        """Prepare pricing model."""
        with suppress(TypeError):
            self.market_data_settings.pricing_model = self.market_data_settings.pricing_model(
                ir_underlyings=[
                    self.market_data_settings.pricing_currencies_map[
                        self.market_data_settings.currency
                    ]
                ],
                pricing_currencies_map=self.market_data_settings.pricing_currencies_map,
                spot_date=self.market_data_settings.spot_date,
                market_data_set_dict=self.data,
                **{
                    f"{self.market_data_settings.asset_class.lower()}_underlyings": [
                        self.market_data_settings.underlying
                    ],
                },
            )

    def _prepare_signal_data(self):
        """Prepare and add signal data to pricing model."""
        # for signal in self.signal_data:
        #     signal_data = signal.prepare_signal_data(
        #         market_data_set_dict=self.market_data_set_dict
        #     )
        #     self.market_data_settings.pricing_model = add_external_signal(
        #         pricing_model=self.market_data_settings.pricing_model,
        #         underlying=signal.signal_name,
        #         data=signal_data,
        #         spot_date=self.market_data_settings.spot_date,
        #         asset_class=self.market_data_settings.asset_class,
        #     )

    def _create_market_snapshot(self):
        """Create market snapshot from pricing model."""
        # self.market_data_settings.pricing_model.calibrate(
        #     dates="all_available_dates",
        #     calibration_type="market",
        #     market_data_set_dict=self.market_data_set_dict,
        # )
        # self.snapshot = self.market_data_settings.pricing_model.get_snapshot(
        #     spot_date=sorted(self.market_data_set_dict.keys())[-1],
        #     case="historical",
        #     when_missing_data="get_previous",
        # )

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
