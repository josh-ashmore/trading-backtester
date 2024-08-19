"""Optimisation Config."""

from enum import Enum
from typing import List, Literal
from pydantic import BaseModel, Field

from modules.optimiser.param_grids.param_grids import ParamGrids


class OptimisationMethod(str, Enum):
    """Optimisation Method Enum."""

    GRID_SEARCH = "grid_search"
    GENETIC_ALGORITHM = "genetic_algorithm"
    BAYESIAN_OPTIMISATION = "bayesian_optimisation"


class Objective(str, Enum):
    """Optimisation Goal Enum."""

    MAXIMISE_RETURN = "maximise_return"
    MINIMISE_RISK = "minimise_risk"
    MAXIMISE_SHARPE_RATIO = "maximise_sharpe_ratio"


class OptimisationConfig(BaseModel):
    """Optimisation Config Model.

    This config controls how the backtester should optimise the
    strategy, such as through parameter sweeps or genetic algorithms.
    """

    config_name: Literal["optimisation"] = Field(
        default="optimisation",
        description="Name of the optimisation configuration.",
    )
    optimisation_method: OptimisationMethod = Field(
        description="Method used for optimisation."
    )
    param_grids: List[ParamGrids]  # should this be a list so we can do multiple passes
    # or just focus on one optimisation at a time?
    objective: Objective = Field(description="Goal of the optimisation process.")
    max_iterations: int = Field(default=100, description="Limit for iterations.")
    early_stopping: bool = Field(default=True, description="Stop if no improvement.")
