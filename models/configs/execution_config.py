"""Execution Config."""

from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ExecutionType(str, Enum):
    """Execution Type Enum."""

    MARKET_ORDER = "market_order"
    LIMIT_ORDER = "limit_order"
    VWAP = "vwap"


class ExecutionConfig(BaseModel):
    """Execution Config Model.

    This config specifies execution strategies such
    as limit orders, market orders, or algorithms like VWAP.

    Should be able to define artificial slippage parameters etc.
    """

    config_name: Literal["execution"] = Field(
        default="execution",
        description="Name of the execution strategy configuration.",
    )
    execution_type: ExecutionType = Field(description="Type of execution strategy.")
    order_size: Optional[float] = Field(
        default=None, description="Order size as a percentage of daily volume."
    )
    slippage_tolerance: Optional[float] = Field(
        default=None, description="Maximum slippage tolerance as a percentage."
    )
