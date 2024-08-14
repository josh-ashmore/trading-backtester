"""Market Data Base Model."""

from pydantic import BaseModel, Field
from datetime import date
from typing import Dict, List, Tuple, Optional


class MarketDataBase(BaseModel):
    """Market Data Base Model."""

    symbol: str = Field(..., description="Instrument symbol or ticker")
    spot_date: date = Field(..., description="Timestamp of the market data")


class MarketDataSpot(MarketDataBase):
    """Market Data Spot Model."""

    price: Optional[float] = Field(None, description="Price of the instrument")
    currency: Optional[str] = Field("USD", description="Currency of the prices")

    class Config:
        orm_mode = True


class VolatilitySurfacePoint(BaseModel):
    """Volaility Surface Point Model."""

    strike: float
    maturity: date
    call_price: Optional[float] = None
    put_price: Optional[float] = None
    call_implied_volatility: Optional[float] = None
    put_implied_volatility: Optional[float] = None


class AggregatedVolatilitySurface(BaseModel):
    """Aggregated Volatility Surface Model."""

    symbol: str
    dates: List[date]
    strikes: List[float]
    maturities: List[date]
    volatilities: Dict[
        Tuple[date, float, date], float
    ]  # (date, strike, maturity) -> volatility

    def get_volatility(self, date: date, strike: float, maturity: date) -> float:
        """
        Retrieve the volatility for a specific date, strike, and maturity.
        """
        return self.volatilities.get((date, strike, maturity))

    def get_strikes(self, date: Optional[date] = None) -> List[float]:
        """
        Get all strikes for a specific date or for the entire period.
        """
        if date:
            return list(
                set(strike for d, strike, _ in self.volatilities.keys() if d == date)
            )
        return self.strikes

    def get_maturities(self, date: Optional[date] = None) -> List[date]:
        """
        Get all maturities for a specific date or for the entire period.
        """
        if date:
            return list(
                set(
                    maturity for d, _, maturity in self.volatilities.keys() if d == date
                )
            )
        return self.maturities

    def get_volatility_surface(self, date: date) -> Dict[Tuple[float, date], float]:
        """
        Get the entire volatility surface for a specific date.
        """
        return {
            (strike, maturity): vol
            for (d, strike, maturity), vol in self.volatilities.items()
            if d == date
        }

    def get_all_volatilities(self) -> List[float]:
        """
        Get all volatilities across all dates, strikes, and maturities.
        """
        return list(self.volatilities.values())


class FXVolatilitySurfacePoint(VolatilitySurfacePoint):
    """FX Volatility Surface Point."""

    delta: Optional[float] = None
