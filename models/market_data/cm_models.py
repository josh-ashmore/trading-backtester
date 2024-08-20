"""CM Data Models."""

from datetime import date
from typing import List, Optional
from pydantic import Field
from models.market_data.base_model import (
    MarketDataSpot,
    VolatilitySurfacePoint,
    MarketDataBase,
)


class CMSpotData(MarketDataSpot):
    """CM Spot Data Model."""

    unit: str = Field(..., description="Unit of the commodity, e.g., ounces, barrels")


class CMFutureData(MarketDataSpot):
    """CM Future Data Model."""

    future_date: date = Field(..., description="Settlement date of the future contract")
    future_price: float = Field(..., description="Future price of the commodity")
    unit: str = Field(..., description="Unit of the commodity, e.g., ounces, barrels")


class CMVolatilitySurfaceData(MarketDataBase):
    """CM Volatility Surface Data Model."""

    surface: List[VolatilitySurfacePoint]


class CMMarketData(MarketDataBase):
    """CM Market Data Model."""

    spot: Optional[List[CMSpotData]] = []
    future: Optional[List[CMFutureData]] = []
    volatility: Optional[List[CMVolatilitySurfaceData]] = []
