"""Market Data Config."""

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class FrequencyTypes(str, Enum):
    """Frequency Types Enum."""

    YEAR = "year"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"


class TransformationTypes(str, Enum):
    """Transformation Types Enum."""

    LOG_RETURN = "log_return"
    MOVING_AVERAGE = "moving_average"


class MarketDataConfig(BaseModel):
    """Market Data Config Model.

    This config can manage how market data is sourced,
    transformed, and used within the backtester.
    """

    config_name: Literal["market_data"] = Field(
        default="market_data",
        description="Name of the market data configuration.",
    )
    data_source: str = Field(
        description="Source of market data, e.g., 'Bloomberg', 'Yahoo Finance'."
    )
    frequency: FrequencyTypes = Field(description="Data frequency.")
    transformations: TransformationTypes = Field(
        default=[],
        description="List of data transformations "
        "(e.g., 'log_return', 'moving_average').",
    )
