"""Trade Enum Models."""

from enum import Enum
from typing import Literal


class DirectionType(str, Enum):
    """Direction Type Enum."""

    BUY = "Buy"
    SELL = "Sell"


class CalcualtionType(str, Enum):
    """Calculation Type Enum."""

    PERCENT_OTM = "percent_otm"
    PERCENT_ITM = "percent_itm"
    PERCENT_ATM = "percent_atm"
    DELTA_NEUTRAL = "delta_neutral"
    ABS = "abs"


InstrumentTypes = Literal["Put", "Call", "Future", "Spot", "Treasury Bill"]


class NotionalRuleType(str, Enum):
    """Notional Rule Type Enum."""

    FIXED = "fixed"
    PERCENTAGE_OF_ACCOUNT = "percentage_of_account"
    DYNAMIC_FORMULA = "dynamic_formula"
