"""Trade Models."""

from datetime import date

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

from models.rules.enums import ActionType

from models.trades.enums import (
    CalcualtionType,
    DirectionType,
    InstrumentTypes,
    NotionalRuleType,
)
from static_data.underlying_data import AssetClass
from models.rules.rules import TradeRule


class NotionalRule(BaseModel):
    """Notional Rule Model."""

    rule_type: NotionalRuleType = Field(
        ..., description="Type of notional rule to apply."
    )
    value: Optional[Union[float, str]] = Field(
        ...,
        description="Value associated with the rule, could be"
        " a fixed amount, percentage, or formula.",
    )


class TradeMessageModel(BaseModel):
    """Trade Message Model."""

    date: date
    message: ActionType
    trade_rule: Optional[TradeRule] = Field(
        default=None, description="Attach the trade rule used to execute this trade."
    )


class BookingModel(BaseModel):
    """Trade Booking Model."""

    trade_date: Optional[date] = None
    value_date: Optional[date] = None
    message: List[TradeMessageModel] = []


class Trade(BookingModel):
    """Base Trade Object."""

    underlying: str
    direction: DirectionType
    instrument_type: InstrumentTypes
    asset_class: AssetClass

    open_price: Optional[float] = Field(
        default=None, description="Open price for the trade."
    )
    close_price: Optional[float] = Field(
        default=None, description="Close price for the trade."
    )
    notional_rule: NotionalRule = Field(..., description="Notional rule for trade.")
    notional_amount: Optional[float] = 0
    number_of_contracts: Optional[int] = Field(
        default=1, description="Number of contracts traded."
    )

    def calculate_pnl(self) -> float:
        """Calculate profit and loss for the trade."""
        if self.close_price is not None:
            if self.direction == "Buy":
                return (self.close_price - self.open_price) * self.number_of_contracts
            else:
                return (self.open_price - self.close_price) * self.number_of_contracts
        return 0.0


class TreasuryBillTrade(Trade):
    """Treasury Bill Trade."""

    instrument_type: Literal["Treasury Bill"] = "Treasury Bill"
    asset_class: AssetClass = AssetClass.FI
    interest_rate: Optional[float] = None


class PutTrade(Trade):
    """Put Trade."""

    premium: float = 0
    instrument_type: Literal["Put"] = "Put"
    strike: Optional[Union[float, int]] = None
    strike_calculation: CalcualtionType = CalcualtionType.ABS


class CallTrade(Trade):
    """Call Trade."""

    premium: float = 0
    instrument_type: Literal["Call"] = "Call"
    strike: Optional[Union[float, int]] = None
    strike_calculation: CalcualtionType = CalcualtionType.ABS
