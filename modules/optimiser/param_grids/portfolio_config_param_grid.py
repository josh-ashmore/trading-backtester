"""Portfolio Config Param Grid."""

from enum import Enum
from typing import List, Dict, Any, Literal
from pydantic import Field

from modules.optimiser.param_grids.base_param_grid import ParamGrid


class PortfolioConfigParams(str, Enum):
    """Portfolio Config Params Enum."""

    ASSET_ALLOCATION = "asset_allocation"
    REBALANCING_FREQUENCY = "rebalancing_frequency"
    LEVERAGE = "leverage"


class PortfolioConfigParamGrid(ParamGrid):
    """Portfolio Config Param Grid Model."""

    model: Literal["portfolio_config"] = "portfolio_config"
    params: Dict[PortfolioConfigParams, List[Any]] = Field(
        description="Dictionary of parameter names and list of possible values."
    )
