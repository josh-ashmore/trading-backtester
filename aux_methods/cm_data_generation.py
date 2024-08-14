"""CM Data Generation."""

from datetime import date, timedelta
import calendar
import random
from aux_methods.helper_methods import generate_date_range
from models.market_data.base_model import VolatilitySurfacePoint
from models.market_data.cm_models import (
    CMMarketData,
    CMSpotData,
    CMFutureData,
    CMVolatilitySurfaceData,
)


def generate_cm_data(symbol: str, start_date: date):
    """Generate CM Data."""
    dates = generate_date_range(start_date=start_date)

    spot_data = []
    future_data = []
    volatility_data = []

    for _date in dates:
        spot = CMSpotData(
            symbol=symbol,
            spot_date=_date,
            price=round(random.uniform(1800, 1900), 2),
            unit="ounces",
        )
        spot_data.append(spot)

        future = CMFutureData(
            symbol=symbol,
            spot_date=_date,
            future_date=_date + timedelta(days=90),
            future_price=round(random.uniform(1820, 1920), 2),
            unit="ounces",
        )
        future_data.append(future)

        volatility = generate_cm_vol_surface_data(symbol=symbol, spot_date=_date)
        volatility_data.append(volatility)

    return CMMarketData(
        symbol=symbol,
        spot_date=start_date,
        spot=spot_data,
        future=future_data,
        volatility=volatility_data,
    )


def generate_cm_vol_surface_data(symbol: str, spot_date: date):
    """Generate CM volatility surface data."""
    spot_rate = round(random.uniform(1, 1.1), 2)
    vol_surface = generate_cm_volatility_surface(
        spot_rate=spot_rate, spot_date=spot_date
    )
    return CMVolatilitySurfaceData(
        spot_date=spot_date, symbol=symbol, surface=vol_surface
    )


def generate_cm_volatility_surface(spot_rate: float, spot_date: date):
    """Generate CM Volatility Surface."""

    def end_of_month(d: date) -> date:
        """End of month."""
        last_day = calendar.monthrange(d.year, d.month)[1]
        return date(d.year, d.month, last_day)

    maturities = []
    current_date = spot_date
    for _ in range(4):
        end_month = end_of_month(current_date)
        maturities.append(end_month)

        if end_month.month == 12:
            next_month = date(end_month.year + 1, 1, 1)
        else:
            next_month = date(end_month.year, end_month.month + 1, 1)
        current_date = next_month

    strikes = [
        spot_rate * m
        for m in [
            800,
            900,
            1_000,
            1_100,
            1_200,
            1_300,
            1_400,
            1_500,
            1_600,
            1_700,
            1_800,
            1_900,
            2_000,
        ]
    ]

    surface_points = []
    for maturity in maturities:
        for strike in strikes:
            call_price = round(random.uniform(100, 1000), 2)
            put_price = round(random.uniform(100, 1000), 2)
            call_iv = round(random.uniform(0.05, 0.25), 4)
            put_iv = round(random.uniform(0.05, 0.25), 4)

            surface_point = VolatilitySurfacePoint(
                strike=strike,
                maturity=maturity,
                call_price=call_price,
                put_price=put_price,
                call_implied_volatility=call_iv,
                put_implied_volatility=put_iv,
            )
            surface_points.append(surface_point)

    return surface_points
