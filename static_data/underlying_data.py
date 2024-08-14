"""Underlying data."""

from typing import Literal
from enum import Enum

StrategyAssetClasses = Literal["FX", "EQ", "CM", "FI", "CC"]
Currencies = Literal["USD", "GBP", "EUR"]
FXUnderlyings = Literal["EURUSD", "USDGBP", "EURGBP"]

FX_UNDERLYINGS = ["EURUSD"]
FI_UNDERLYINGS = ["US10Y"]
EQ_UNDERLYINGS = ["AAPL"]
CC_UNDERLYINGS = ["BTC"]
CM_UNDERLYINGS = ["GOLD"]


class AssetClass(str, Enum):
    """Asset Class Enum."""

    FX = "FX"
    EQ = "EQ"
    CM = "CM"
    FI = "FI"
    CC = "CC"
