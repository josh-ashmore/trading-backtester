"""Execution Rule Param Grid Models."""

from enum import Enum
from typing import List, Dict, Any, Literal
from pydantic import Field

from modules.optimiser.param_grids.base_param_grid import ParamGrid


class ExecutionRuleParams(str, Enum):
    """Execution Rule Params Enum."""

    TARGET_COST = "target_cost"


class ExecutionRuleParamGrid(ParamGrid):
    """Execution Rule Param Grid Model."""

    model: Literal["execution_rule"] = "execution_rule"
    params: Dict[ExecutionRuleParams, List[Any]] = Field(
        description="Dictionary of parameter names and list of possible values."
    )
