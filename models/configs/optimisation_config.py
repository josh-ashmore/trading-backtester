"""Optimisation Config."""

from enum import Enum
from typing import Dict, List, Literal
from pydantic import BaseModel, Field


class OptimisationMethod(str, Enum):
    """Optimisation Method Enum."""

    GRID_SEARCH = "grid_search"
    GENETIC_ALGORITHM = "genetic_algorithm"
    BAYESIAN_OPTIMISATION = "bayesian_optimisation"


class Objective(str, Enum):
    """Optimisation Goal Enum."""

    MAXIMISE_RETURN = "maximise_return"
    MINIMISE_RISK = "minimise_risk"
    SHARPE_RATIO = "sharpe_ratio"


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
    parameter_grid: Dict[str, List[float]] = Field(
        description="Parameters to optimise with their respective ranges or values."
    )
    objective: Objective = Field(description="Goal of the optimisation process.")
    max_iterations: int = Field(default=100, description="Limit for iterations.")
    early_stopping: bool = Field(default=True, description="Stop if no improvement.")
