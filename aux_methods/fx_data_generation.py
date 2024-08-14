"""FX Data Generation."""

from datetime import date, timedelta
import random
from aux_methods.helper_methods import generate_date_range
from models.market_data.base_model import FXVolatilitySurfacePoint
from models.market_data.fx_models import (
    FXMarketData,
    FXSpotData,
    FXForwardData,
    FXVolatilitySurfaceData,
)


def generate_fx_data(symbol: str, start_date: date):
    """Generate FX Data."""
    dates = generate_date_range(start_date=start_date)

    spot_data = []
    forward_data = []
    volatility_data = []

    for _date in dates:
        spot = FXSpotData(
            symbol=symbol,
            spot_date=_date,
            price=round(random.uniform(0.9, 1.1), 4),
        )
        spot_data.append(spot)

        forward = FXForwardData(
            symbol=symbol,
            spot_date=_date,
            forward_date=_date + timedelta(days=90),
            forward_rate=round(random.uniform(0.95, 1.2), 4),
        )
        forward_data.append(forward)

        volatility = generate_fx_vol_surface_data(symbol=symbol, start_date=_date)
        volatility_data.append(volatility)

    return FXMarketData(
        symbol=symbol,
        spot_date=start_date,
        spot=spot_data,
        forward=forward_data,
        volatility=volatility_data,
    )


def generate_fx_vol_surface_data(symbol: str, start_date: date):
    """Generate FX volatility surface data."""
    spot_rate = round(random.uniform(0.9, 1.1), 4)
    vol_surface = generate_fx_volatility_surface(
        spot_rate=spot_rate, spot_date=start_date
    )
    return FXVolatilitySurfaceData(
        spot_date=start_date, symbol=symbol, surface=vol_surface
    )


def generate_fx_volatility_surface(spot_rate: float, spot_date: date):
    maturities = [spot_date + timedelta(days=i) for i in [30, 90, 180, 365]]
    strikes = [spot_rate * m for m in [0.8, 0.9, 1.0, 1.1, 1.2]]

    surface_points = []
    for maturity in maturities:
        for strike in strikes:
            call_price = round(random.uniform(0.001, 0.01), 4)
            put_price = round(random.uniform(0.001, 0.01), 4)
            call_iv = round(random.uniform(0.05, 0.25), 4)
            put_iv = round(random.uniform(0.05, 0.25), 4)
            delta = round(random.uniform(-0.5, 0.5), 4)

            surface_point = FXVolatilitySurfacePoint(
                strike=strike,
                maturity=maturity,
                call_price=call_price,
                put_price=put_price,
                call_implied_volatility=call_iv,
                put_implied_volatility=put_iv,
                delta=delta,
            )
            surface_points.append(surface_point)

    return surface_points
