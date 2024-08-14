"""EQ Data Models."""

from datetime import date
from typing import List, Optional

from pydantic import Field
from models.market_data.base_model import (
    MarketDataBase,
    MarketDataSpot,
    VolatilitySurfacePoint,
)


class EQSpotData(MarketDataSpot):
    """EQ Spot Data."""

    pass


class EQFutureData(MarketDataSpot):
    """EQ Futures Data."""

    future_date: date = Field(..., description="Settlement date of the future contract")
    future_price: float = Field(..., description="Future price of the stock")


class EQVolatilitySurfaceData(MarketDataBase):
    """EQ Volatility Surface Data Model."""

    surface: List[VolatilitySurfacePoint]


class EQMarketData(MarketDataBase):
    """EQ Market Data Model."""

    spot: Optional[List[EQSpotData]] = []
    future: Optional[List[EQFutureData]] = []
    volatility: Optional[List[EQVolatilitySurfaceData]] = []
