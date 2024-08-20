"""FI Data Generation."""

from datetime import timedelta, date
import random
from aux_methods.helper_methods import generate_date_range
from models.market_data.fi_models import (
    FISpotData,
    FIForwardData,
    FIYieldCurveData,
    FIMarketData,
)


def generate_fi_data(symbol: str, start_date: date):
    """Generate FI Data."""
    dates = generate_date_range(start_date=start_date)

    spot_data = []
    forward_data = []
    yield_curve_data = []

    for _date in dates:
        spot = FISpotData(
            symbol=symbol, spot_date=_date, price=round(random.uniform(95, 105), 2)
        )
        spot_data.append(spot)

        forward = FIForwardData(
            symbol=symbol,
            spot_date=_date,
            forward_date=_date + timedelta(days=90),
            forward_price=round(random.uniform(96, 106), 2),
        )
        forward_data.append(forward)

        yield_curve = generate_yield_curve_with_tbills(symbol=symbol, date=_date)
        yield_curve_data.append(yield_curve)

    return FIMarketData(
        spot_date=start_date,
        symbol=symbol,
        spot=spot_data,
        forward=forward_data,
        yield_curve=yield_curve_data,
    )


def generate_yield_curve_with_tbills(symbol: str, date: date):
    """Generate Yield Curve including T-Bill data."""
    # TODO: split this into respective underlyings

    # Maturities for standard yield curve (e.g., 1 year to 5 years)
    standard_maturity_dates = [date + timedelta(days=365 * i) for i in range(1, 6)]

    # Generate yields for standard maturities
    standard_yields = [
        round(random.uniform(0.01, 0.05), 4) for _ in standard_maturity_dates
    ]

    # Maturities for T-Bills (e.g., 1 month, 3 months, 6 months, and 1 year)
    tbill_maturity_dates = [
        date + timedelta(days=30),
        date + timedelta(days=90),
        date + timedelta(days=180),
        date + timedelta(days=365),
    ]

    # Generate yields for T-Bills (shorter-term)
    tbill_yields = [round(random.uniform(0.005, 0.03), 4) for _ in tbill_maturity_dates]

    # Combine all maturity dates and yields
    combined_maturity_dates = tbill_maturity_dates + standard_maturity_dates
    combined_yields = tbill_yields + standard_yields

    # Create the yield curve data object
    yield_curve = FIYieldCurveData(
        symbol=symbol,
        spot_date=date,
        maturity_dates=combined_maturity_dates,
        yields=combined_yields,
    )

    return yield_curve
