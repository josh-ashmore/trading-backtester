"""Optimiser Manager."""

from copy import deepcopy
import itertools
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple
from pydantic import BaseModel, model_validator

from models.configs.optimisation_config import Objective, OptimisationConfig
from models.input.input import BaseStrategyInput
from models.output.output import BacktesterOutput
from modules.optimiser.param_grids.base_param_grid import ParamGrid

if TYPE_CHECKING:
    from modules.orchestrator import BacktesterOrchestrator


class OptimiserManager(BaseModel):
    """Optimiser Manager Module."""

    optimiser_config: OptimisationConfig
    strategy_input: BaseStrategyInput
    backtester: "BacktesterOrchestrator"
    best_result: Optional[BacktesterOutput] = None
    best_input: Optional[BaseStrategyInput] = None

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if self.best_result is None:
            self.best_result = BacktesterOutput()
        return self

    def run_optimisation(self):
        """Run the optimisation process."""
        for input in self.generate_strategy_inputs():
            self.backtester.strategy_input = input
            self.backtester.run_backtest()
            result = self.backtester.results
            if self.is_better_result(result):
                self.best_result = result
                self.best_input = input
        return self.best_input, self.best_result

    def generate_param_combinations(self, param_grids: List[ParamGrid]):
        """Generate param combinations from param grid models."""
        combinations = []
        for grid in param_grids:
            keys, values = zip(*grid.params.items())
            for combo in itertools.product(*values):
                combinations.append((grid.model, dict(zip(keys, combo))))
        return combinations

    def apply_combinations_to_strategy_inputs(
        self,
        base_strategy_input: BaseStrategyInput,
        param_combinations: List[Tuple[str, Dict]],
    ) -> List[BaseStrategyInput]:
        """Return list of strategy inputs."""
        strategy_inputs = []
        for model_name, params in param_combinations:
            strategy_input = deepcopy(base_strategy_input)
            match model_name:
                case "execution_rule":
                    for trade_rule_setting in strategy_input.trade_rule_settings:
                        for execution_rule in trade_rule_setting.execution_rules:
                            for key, value in params.items():
                                setattr(execution_rule, key.value, value)
                case "execution_config" | "portfolio_config":
                    for key, value in params.items():
                        setattr(execution_rule, key.value, value)

            strategy_inputs.append(strategy_input)

        return strategy_inputs

    def generate_strategy_inputs(
        self, base_strategy_input, param_grids
    ) -> List[BaseStrategyInput]:
        """Combine combinations and calculate all input models."""
        param_combinations = self.generate_param_combinations(param_grids=param_grids)
        strategy_inputs = self.apply_combinations_to_strategy_inputs(
            base_strategy_input=base_strategy_input,
            param_combinations=param_combinations,
        )
        return strategy_inputs

    def is_better_result(self, result: BacktesterOutput):
        """Compare current result with the best result based on the objective."""
        if not self.best_result:
            return True
        match self.optimiser_config.objective:
            case Objective.MAXIMISE_RETURN:
                return result.returns[-1] > self.best_result.returns[-1]
            case Objective.MINIMISE_RISK:
                return result.max_drawdown < self.best_result.max_drawdown
            case Objective.MAXIMISE_SHARPE_RATIO:
                return result.sharpe_ratio > self.best_result.sharpe_ratio
        return False
