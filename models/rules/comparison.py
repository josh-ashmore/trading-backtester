"""Second attempt at rules logic.

The aim is to give the user the ability to compare
two sets of data:

    trade data
    market data
    signal data
    date data <- can this be combined into other models?

So that they are able to do things like:

OPEN
    date -> current
    ==
    market -> expiry

CLOSE
    trade -> value_date
    >
    market -> expiry_date + offset

OPEN
    market -> spot
    >=
    5_000
"""

from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any, Literal, Optional, Union
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.rules.enums import ActionType
from models.trades.schedule import TradeSchedule
from static_data.underlying_data import AssetClass

if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel
    from models.rules.execution import Trades


class DateOffsetType(str, Enum):
    """Date Offset Type."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class DateSettings(BaseModel):
    """Date Settings Model."""

    settings_name: Literal["date_settings"] = "date_settings"
    offset: int = Field(default=0, description="Offset date by amount.")
    offset_type: DateOffsetType = Field(default="day", description="Type of offset.")
    offset_value: Optional[timedelta | relativedelta] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FieldType(str, Enum):
    """Field Type Enum."""

    VALUE = "value"
    DATE = "date"


class TradeField(BaseModel):
    """Trade Field Model."""

    field_name: Literal["trade"] = "trade"
    field: str = Field(description="Choice of trade object fields.")
    field_type: FieldType = Field(
        description="Field type to determine additional checks."
    )

    def return_value(
        self,
        date: date,
        data: Optional["MarketModel"] = None,
        trade: Optional["Trades"] = None,
        trade_schedule: Optional[TradeSchedule] = None,
    ):
        """Return value."""
        return getattr(trade, self.field)


class MarketField(BaseModel):
    """Market Field Model."""

    field_name: Literal["market"] = "market"
    field: str = Field(description="Choice of market data object fields.")
    field_type: FieldType = Field(
        description="Field type to determine additional checks."
    )
    underlying: str
    asset_class: AssetClass

    def return_value(
        self,
        date: date,
        data: Optional["MarketModel"] = None,
        trade: Optional["Trades"] = None,
        trade_schedule: Optional[TradeSchedule] = None,
    ):
        """Return value."""
        return data.get(
            market_variable=self.field,
            underlying=self.underlying,
            date=date,
            asset_class=self.asset_class,
        )


class DateFieldType(str, Enum):
    """Date Field Type."""

    CURRENT = "current"
    EXPIRY = "expiry"


class DateField(BaseModel):
    """Date Field."""

    field_name: Literal["date"] = "date"
    field: DateFieldType = Field(description="Choice of date data object fields.")
    field_type: FieldType = FieldType.DATE

    def return_value(
        self,
        date: date,
        data: Optional["MarketModel"] = None,
        trade: Optional["Trades"] = None,
        trade_schedule: Optional[TradeSchedule] = None,
    ):
        """Return value."""
        match self.field:
            case DateFieldType.CURRENT:
                return date
            case DateFieldType.EXPIRY:
                assert data and trade
                return data.get_next_expiry(
                    underlying=trade.underlying,
                    date=date,
                    asset_class=trade.asset_class,
                    instrument_type=trade.instrument_type,
                )


class ValueField(BaseModel):
    """Value Field."""

    field_name: Literal["value"] = "value"
    value: float
    field_type: FieldType = FieldType.VALUE

    def return_value(
        self,
        date: date,
        data: Optional["MarketModel"] = None,
        trade: Optional["Trades"] = None,
        trade_schedule: Optional[TradeSchedule] = None,
    ):
        """Return value."""
        return self.value


class PortfolioFieldType(str, Enum):
    """Portfolio Field Type."""

    OPEN_TRADES = "open_trades"
    NO_OPEN_TRADES = "no_open_trades"


class PortfolioField(BaseModel):
    """Portfolio Field."""

    field_name: Literal["portfolio"] = "portfolio"
    field: PortfolioFieldType
    field_type: FieldType = FieldType.VALUE

    def return_value(
        self,
        date: date,
        data: Optional["MarketModel"] = None,
        trade: Optional["Trades"] = None,
        trade_schedule: Optional[TradeSchedule] = None,
    ):
        """Return value."""
        match self.field:
            case PortfolioFieldType.OPEN_TRADES:
                return np.any(
                    [
                        trade
                        for trade in trade_schedule.trades
                        if trade.message[-1].message == ActionType.OPEN
                    ]
                )
            case PortfolioFieldType.NO_OPEN_TRADES:
                return not np.any(
                    [
                        trade
                        for trade in trade_schedule.trades
                        if trade.message[-1].message == ActionType.OPEN
                    ]
                )


FieldSettings = Annotated[
    Union[TradeField | MarketField | DateField | ValueField | PortfolioField],
    Field(..., discriminator="field_name"),
]

AdditionalSettings = Annotated[
    Union[DateSettings], Field(..., discriminator="settings_name")
]


class ComparisonField(BaseModel):
    """A Model."""

    field_settings: FieldSettings
    additional_settings: Optional[AdditionalSettings] = None

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        match self.field_settings.field_type:
            case FieldType.DATE:
                if not self.additional_settings:
                    self.additional_settings = DateSettings()
        return self

    def return_value(
        self,
        date: date,
        data: Optional["MarketModel"] = None,
        trade: Optional["Trades"] = None,
        trade_schedule: Optional[TradeSchedule] = None,
    ):
        """Return value."""
        value = self.field_settings.return_value(
            date=date, data=data, trade=trade, trade_schedule=trade_schedule
        )
        return self.apply_settings(value=value)

    def apply_settings(self, value: Any):
        """Apply settings to value."""
        match self.field_settings.field_type:
            case FieldType.DATE:
                offset_type = {
                    DateOffsetType.DAY: timedelta(days=self.additional_settings.offset),
                    DateOffsetType.WEEK: relativedelta(
                        weeks=self.additional_settings.offset
                    ),
                    DateOffsetType.MONTH: relativedelta(
                        months=self.additional_settings.offset
                    ),
                    DateOffsetType.YEAR: relativedelta(
                        years=self.additional_settings.offset
                    ),
                }
                return value + offset_type[self.additional_settings.offset_type]
            case FieldType.VALUE:
                return value
