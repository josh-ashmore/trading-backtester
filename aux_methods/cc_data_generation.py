"""FI Data Generation."""

from datetime import date, timedelta
import random
from aux_methods.helper_methods import generate_date_range
from models.market_data.cc_models import (
    CCSpotData,
    CCForwardData,
    CCMarketData,
    CCVolatilityData,
)


def generate_cc_data(symbol: str, start_date: date):
    dates = generate_date_range(start_date)

    spot_data = []
    forward_data = []
    volatility_data = []

    for _date in dates:
        spot = CCSpotData(
            symbol=symbol, spot_date=_date, price=round(random.uniform(30000, 40000), 2)
        )
        spot_data.append(spot)

        forward = CCForwardData(
            symbol=symbol,
            spot_date=_date,
            forward_date=_date + timedelta(days=30),
            forward_price=round(random.uniform(31000, 41000), 2),
        )
        forward_data.append(forward)

        volatility = CCVolatilityData(
            symbol=symbol,
            spot_date=_date,
            maturity_date=_date + timedelta(days=30),
            volatility=round(random.uniform(0.5, 1.0), 4),
        )
        volatility_data.append(volatility)

    return CCMarketData(
        spot_date=start_date,
        symbol=symbol,
        spot=spot_data,
        forward=forward_data,
        volatility=volatility_data,
    )
