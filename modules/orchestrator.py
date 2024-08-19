"""Orchestrator Module."""

from typing import Optional
from pydantic import BaseModel, model_validator

from models.input.input import BaseStrategyInput
from models.output.output import BacktesterOutput
from modules.optimiser.optimiser_manager import OptimiserManager
from modules.risk_management_manager import RiskManager
from modules.stream_manager import StreamManager
from modules.trade_manager import TradeManager


class OrchestratorManagers(BaseModel):
    """Orchestrator Managers."""

    stream_manager: Optional[StreamManager] = None
    trade_manager: Optional[TradeManager] = None
    optimiser_manager: Optional[OptimiserManager] = None
    risk_manager: Optional[RiskManager] = None


class BacktesterOrchestrator(OrchestratorManagers):
    """Backtester Orchestrator Model."""

    strategy_input: BaseStrategyInput
    results: Optional[BacktesterOutput] = None

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        self._validate_risk_manager()
        self._validate_stream_manager()
        self._validate_optimisation_manager()
        self._validate_trade_manager()
        self._setup_results_model()
        return self

    def _setup_results_model(self):
        """Set-up results model."""
        if self.results is None:
            self.results = BacktesterOutput()

    def _validate_trade_manager(self):
        """Validate trade manager."""
        self.trade_manager = TradeManager(
            trade_rule_settings=self.strategy_input.trade_rule_settings
        )

    def _validate_stream_manager(self):
        """Validate stream manager if config provided."""
        stream_config = next(
            (
                config
                for config in self.strategy_input.configs
                if config.config_name == "stream"
            ),
            None,
        )
        if stream_config:
            self.stream_manager = StreamManager(
                stream_config=stream_config,
                trades_to_open=[
                    trade_rule for trade_rule in self.strategy_input.trade_rule_settings
                ],
            )

    def _validate_optimisation_manager(self):
        """Validate optimisation manager if config provided."""
        optimiser_config = next(
            (
                config
                for config in self.strategy_input.configs
                if config.config_name == "optimisation"
            ),
            None,
        )
        if optimiser_config:
            self.optimiser_manager = OptimiserManager(
                optimiser_config=optimiser_config,
                strategy_input=self.strategy_input,
                backtester=self,
            )

    def _validate_risk_manager(self):
        """Validate risk manager if config provided."""
        risk_config = next(
            (
                config
                for config in self.strategy_input.configs
                if config.config_name == "risk_management"
            ),
            None,
        )
        if risk_config:
            self.stream_manager = RiskManager(risk_config=risk_config)

    def run(self):
        """Main method to run the backtest or optimization."""
        if self.optimiser_manager:
            return self.optimiser_manager.run_optimisation()
        else:
            return self.run_backtest()

    def run_backtest(self):
        """Run backtest."""
        data = self.strategy_input.data
        for current_date in self.iterate_dates():
            self.trade_manager.execute_trades(
                current_date=current_date,
                data=data,
                account=self.strategy_input.account,
            )
            if self.stream_manager:
                self.stream_manager.roll_streams(
                    current_date=current_date,
                    trades=self.strategy_input.get_trades_to_execute(),
                )
            if self.risk_manager:
                self.risk_manager.apply_risk_management(
                    self.strategy_input.account,
                    self.trade_manager.backtester_trades.get_live_trades(),
                )
        self.results.evaluate(
            trades=self.trade_manager.backtester_trades.trades,
            account=self.strategy_input.account,
            risk_free_rate=0,
        )

    def iterate_dates(self):
        """Method to return dates to iterate over."""
        return self.strategy_input.dates
