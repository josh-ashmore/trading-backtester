"""Market Data Config."""

from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, List, Literal
import numpy as np
from pydantic import BaseModel, Field

from static_data.underlying_data import AssetClass

if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel
    from models.market_data.base_model import MarketDataBase


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


class DataSource(BaseModel):
    """Data Source Model."""

    market_variable_name: str
    underlying: str
    asset_class: AssetClass


class SubTransformation(BaseModel):
    """Sub Transformation Model."""

    frequency: FrequencyTypes = Field(..., description="Data frequency.")
    transformation_type: TransformationTypes = Field(
        ..., description="Transformation type."
    )


class Transformation(BaseModel):
    """Transformation Model."""

    data_source: DataSource = Field(
        ...,
        description="A data source object to point "
        "towards the required data to transform.",
    )
    sub_transformations: List[SubTransformation] = Field(
        default=[],
        description="List of data transformations "
        "(e.g., 'log_return', 'moving_average').",
    )


class MarketDataConfig(BaseModel):
    """Market Data Config Model.

    This config can manage how market data is sourced,
    transformed, and used within the backtester.
    """

    config_name: Literal["market_data"] = Field(
        default="market_data",
        description="Name of the market data configuration.",
    )
    transformations: List[Transformation] = Field(
        ..., description="A list of transformations to apply to market data sources."
    )

    def apply_transformations(self, market_data: "MarketModel"):
        """Apply the transformations as per the market data config."""
        for transformation in self.transformations:
            for sub_transformation in transformation.sub_transformations:
                target_data = getattr(
                    getattr(market_data, transformation.data_source.asset_class)[
                        transformation.data_source.underlying
                    ],
                    transformation.data_source.market_variable_name,
                )
                transformation_type = sub_transformation.transformation_type
                match transformation_type:
                    case TransformationTypes.LOG_RETURN:
                        self.calculate_log_return(data=deepcopy(target_data))
                    case TransformationTypes.MOVING_AVERAGE:
                        self.calculate_moving_average(
                            data=deepcopy(data=deepcopy(target_data))
                        )
                    case _:
                        raise NotImplementedError(
                            f"{transformation_type} is not yet implemented."
                        )

    def calculate_log_return(data: List["MarketDataBase"]):
        """Calculate log returns for a list of AssetPriceData objects."""
        for i in range(1, len(data)):
            current_price = data[i].price
            previous_price = data[i - 1].price
            setattr(data[i], "log_return", np.log(current_price / previous_price))

    def calculate_moving_average(data: List["MarketDataBase"], window: int):
        """Calculate moving average for a list of AssetPriceData objects."""
        for i in range(window - 1, len(data)):
            window_prices = [data[j].price for j in range(i - window + 1, i + 1)]
            setattr(data[i], f"{window}_moving_average", np.mean(window_prices))
