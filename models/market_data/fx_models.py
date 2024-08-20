"""FX Data Models."""

from pydantic import Field
from typing import List, Optional
from datetime import date

from models.market_data.base_model import (
    FXVolatilitySurfacePoint,
    MarketDataBase,
    MarketDataSpot,
)


class FXSpotData(MarketDataSpot):
    """FX Spot Data Model."""

    pass


class FXForwardData(MarketDataSpot):
    """FX Forward Data Model."""

    forward_date: date = Field(
        ..., description="Settlement date of the forward contract"
    )
    forward_rate: float = Field(..., description="Forward exchange rate")


class FXVolatilitySurfaceData(MarketDataBase):
    """FX Volatility Surface Data Model."""

    surface: List[FXVolatilitySurfacePoint] = Field(
        ..., description="List of volatility surface points"
    )


class FXMarketData(MarketDataBase):
    """FX Market Data Model."""

    spot: Optional[List[FXSpotData]] = Field(
        default_factory=list, description="List of spot rate data"
    )
    forward: Optional[List[FXForwardData]] = Field(
        default_factory=list, description="List of forward rate data"
    )
    volatility: Optional[List[FXVolatilitySurfaceData]] = Field(
        default_factory=list, description="List of volatility surface data"
    )
