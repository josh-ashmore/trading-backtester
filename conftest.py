"""Conftest file."""

from datetime import date
import pytest

from aux_methods.cc_data_generation import generate_cc_data
from aux_methods.cm_data_generation import generate_cm_data
from aux_methods.eq_data_generation import generate_eq_data
from aux_methods.fi_data_generation import generate_fi_data
from aux_methods.fx_data_generation import generate_fx_data
from models.market_data.market_model import MarketModel
from static_data.underlying_data import (
    CM_UNDERLYINGS,
    CC_UNDERLYINGS,
    EQ_UNDERLYINGS,
    FX_UNDERLYINGS,
    FI_UNDERLYINGS,
)


@pytest.fixture(scope="session")
def market_data():
    """Market data."""
    start_date = date(2024, 1, 1)

    cm_data = {}
    for underlying in CM_UNDERLYINGS:
        cm_data[underlying] = generate_cm_data(symbol=underlying, start_date=start_date)

    eq_data = {}
    for underlying in EQ_UNDERLYINGS:
        eq_data[underlying] = generate_eq_data(symbol=underlying, start_date=start_date)

    fx_data = {}
    for underlying in FX_UNDERLYINGS:
        fx_data[underlying] = generate_fx_data(symbol=underlying, start_date=start_date)

    fi_data = {}
    for underlying in FI_UNDERLYINGS:
        fi_data[underlying] = generate_fi_data(symbol=underlying, start_date=start_date)

    cc_data = {}
    for underlying in CC_UNDERLYINGS:
        cc_data[underlying] = generate_cc_data(symbol=underlying, start_date=start_date)

    return MarketModel(
        FX=fx_data,
        EQ=eq_data,
        FI=fi_data,
        CM=cm_data,
        CC=cc_data,
    )
