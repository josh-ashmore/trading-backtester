"""Execution Config Param Grid."""

from enum import Enum
from typing import List, Dict, Any, Literal
from pydantic import Field

from modules.optimiser.param_grids.base_param_grid import ParamGrid


class ExecutionConfigParams(str, Enum):
    """Execution Config Params Enum."""

    ORDER_SIZE = "order_size"
    SLIPPAGE_TOLERANCE = "slippage_tolerance"


class ExecutionConfigParamGrid(ParamGrid):
    """Execution Config Param Grid Model."""

    model: Literal["execution_config"] = "execution_config"
    params: Dict[ExecutionConfigParams, List[Any]] = Field(
        description="Dictionary of parameter names and list of possible values."
    )
