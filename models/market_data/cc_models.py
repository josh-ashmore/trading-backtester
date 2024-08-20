"""CC Data Models."""

from datetime import date
from typing import Optional, List

from pydantic import Field
from models.market_data.base_model import MarketDataBase, MarketDataSpot


class CCSpotData(MarketDataSpot):
    """CC Spot Data Model."""

    pass


class CCForwardData(MarketDataSpot):
    """CC Forward Data Model."""

    forward_date: date = Field(
        ..., description="Settlement date of the forward contract"
    )
    forward_price: float = Field(..., description="Forward price of the cryptocurrency")


class CCVolatilityData(MarketDataBase):
    """CC Volatility Data Model."""

    maturity_date: date = Field(
        ..., description="Maturity date for the volatility quote"
    )
    volatility: float = Field(..., description="Implied volatility")


class CCMarketData(MarketDataBase):
    """CC Market Data Model."""

    spot: Optional[List[CCSpotData]] = []
    forward: Optional[List[CCForwardData]] = []
    volatility: Optional[List[CCVolatilityData]] = []
