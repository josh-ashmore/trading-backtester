"""EQ Data Generation."""

from datetime import date, timedelta
import random
from aux_methods.helper_methods import generate_date_range, generate_volatility_surface
from models.market_data.eq_models import (
    EQMarketData,
    EQSpotData,
    EQFutureData,
    EQVolatilitySurfaceData,
)


def generate_eq_data(symbol: str, start_date: date):
    """Generate EQ Data."""
    dates = generate_date_range(start_date=start_date)

    spot_data = []
    future_data = []
    volatility_data = []

    for _date in dates:
        spot = EQSpotData(
            symbol=symbol,
            spot_date=_date,
            price=round(random.uniform(500, 600), 2),
        )
        spot_data.append(spot)

        future = EQFutureData(
            symbol=symbol,
            spot_date=_date,
            future_date=_date + timedelta(days=90),
            future_price=round(random.uniform(720, 820), 2),
        )
        future_data.append(future)

        volatility = generate_eq_vol_surface_data(symbol=symbol, start_date=_date)
        volatility_data.append(volatility)

    return EQMarketData(
        symbol=symbol,
        spot_date=start_date,
        spot=spot_data,
        future=future_data,
        volatility=volatility_data,
    )


def generate_eq_vol_surface_data(symbol: str, start_date: date):
    """Generate EQ volatility surface data."""
    spot_price = round(random.uniform(500, 600), 2)
    vol_surface = generate_volatility_surface(
        spot_price=spot_price, spot_date=start_date
    )
    return EQVolatilitySurfaceData(
        spot_date=start_date, symbol=symbol, surface=vol_surface
    )
