"""Param Grids."""

from typing import Annotated, Union

from pydantic import Field
from modules.optimiser.param_grids.execution_config_param_grid import (
    ExecutionConfigParamGrid,
)
from modules.optimiser.param_grids.execution_rule_param_grid import (
    ExecutionRuleParamGrid,
)
from modules.optimiser.param_grids.portfolio_config_param_grid import (
    PortfolioConfigParamGrid,
)

# need param grids for risk management and stream configs
# need methods in each param grid to correctly match up keys/values to attributes
ParamGrids = Annotated[
    Union[ExecutionRuleParamGrid, ExecutionConfigParamGrid, PortfolioConfigParamGrid],
    Field(..., discriminator="model"),
]
