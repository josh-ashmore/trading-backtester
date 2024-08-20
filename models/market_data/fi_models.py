"""FI Data Models."""

from datetime import date
from typing import List, Optional

from pydantic import Field

from models.market_data.base_model import MarketDataBase, MarketDataSpot


class FISpotData(MarketDataSpot):
    """FI Spot Data Model."""

    pass


class FIForwardData(MarketDataSpot):
    """FI Forward Data Model."""

    forward_date: date = Field(
        ..., description="Settlement date of the forward contract"
    )
    forward_price: float = Field(..., description="Forward price of the bond")


class FIYieldCurveData(MarketDataBase):
    """FI Yield Curve Data Model."""

    maturity_dates: list[date] = Field(..., description="List of bond maturities")
    yields: list[float] = Field(
        ..., description="Corresponding yields for each maturity"
    )


class FIMarketData(MarketDataBase):
    """FI Market Data Model."""

    spot: Optional[List[FISpotData]] = []
    forward: Optional[List[FIForwardData]] = []
    yield_curve: Optional[List[FIYieldCurveData]] = []
