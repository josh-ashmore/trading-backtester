"""Helper generation methods."""

from datetime import datetime, timedelta
import random
from typing import List
from models.market_data.base_model import (
    AggregatedVolatilitySurface,
    VolatilitySurfacePoint,
)
from models.market_data.cm_models import CMVolatilitySurfaceData


def generate_date_range(start_date: datetime, days: int = 120):
    """Generate date range."""
    return [start_date + timedelta(days=i) for i in range(days)]


def generate_volatility_surface(spot_price: float, spot_date: datetime):
    """Generate volaility surface data."""
    maturities = [spot_date + timedelta(days=i) for i in [30, 90, 180, 365]]
    strikes = [spot_price * m for m in [0.8, 0.9, 1.0, 1.1, 1.2]]

    surface_points = []
    for maturity in maturities:
        for strike in strikes:
            volatility = round(random.uniform(0.15, 0.35), 4)
            surface_point = VolatilitySurfacePoint(
                strike=strike, maturity=maturity, volatility=volatility
            )
            surface_points.append(surface_point)

    return surface_points


def aggregate_vol_surface_data(
    vol_surface_data: List[CMVolatilitySurfaceData],
    symbol: str,
) -> AggregatedVolatilitySurface:
    strikes = set()
    maturities = set()
    volatilities = {}

    for day_data in vol_surface_data:
        for point in day_data.surface:
            strikes.add(point.strike)
            maturities.add(point.maturity)
            volatilities[(day_data.spot_date, point.strike, point.maturity)] = (
                point.volatility
            )

    aggregated_surface = AggregatedVolatilitySurface(
        symbol=symbol,
        dates=[data.spot_date for data in vol_surface_data],
        strikes=sorted(strikes),
        maturities=sorted(maturities),
        volatilities=volatilities,
    )

    return aggregated_surface
