"""Simple Backtester Module."""

from datetime import date
import itertools
from typing import Optional
from pydantic import BaseModel, model_validator

from models.configs.optimisation_config import OptimisationConfig
from models.input.input import BaseStrategyInput
from models.market_data.market_model import MarketModel
from models.output.output import BacktesterOutput
from models.rules.rules import TradeRule
from models.rules.execution import (
    ExecutionRule,
    TradeMessageModel,
    Trades,
)
from models.trades.schedule import TradeSchedule
from modules.stream_manager import Stream


class Backtester(BaseModel):
    """Main Backtester Module.


    Handles all logic for running a backtest
    given user input.
    """

    strategy_input: BaseStrategyInput

    backtester_trades: Optional[TradeSchedule] = None
    strategy_output: Optional[BacktesterOutput] = None

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if not self.backtester_trades:
            self.backtester_trades = TradeSchedule(trades=[])
        if not self.strategy_output:
            self.strategy_output = BacktesterOutput()
        return self

    def run(self):
        """Run backtester module."""
        if [
            isinstance(config, OptimisationConfig)
            for config in self.strategy_input.configs
        ]:
            self._run_optimisation()
        else:
            self._run_strategy()

    def _run_strategy(self):
        """Run strategy using user inputs."""
        for _date in self.strategy_input.dates:
            self._manage_open_trades(data=self.strategy_input.data, date=_date)
            self._evaluate_new_trades(data=self.strategy_input.data, date=_date)

    # STREAMS

    def manage_streams(self, current_date):
        # Iterate over active streams and check if they need to roll
        for stream in self.active_streams:
            if self.is_roll_due(stream, current_date):
                self.roll_stream(stream, current_date)

        # If fewer than the configured number of streams are active, open new streams
        while len(self.active_streams) < self.stream_config.num_streams:
            self.open_new_stream(current_date)

    def roll_stream(self, stream, current_date):
        # Close the existing position
        self.close_position(stream.position)

        # Open a new position for this stream
        self.open_new_position(stream, current_date)

    def open_new_stream(self, current_date):
        # Logic to open a new stream, potentially setting its open date to current_date
        new_position = self.open_position(current_date)
        self.active_streams.append(
            Stream(position=new_position, open_date=current_date)
        )

    # OPTIMISATION

    def _run_optimisation(self, optimisation_config: OptimisationConfig):
        """Run optimisation."""
        best_score = float("-inf")
        best_params = None
        iterations = 0

        for params in self._generate_param_combinations(
            optimisation_config.parameter_grid
        ):
            self._apply_params(params)
            score = self._run_strategy()
            # how do we actually get a score - this should be a method that
            # looks at the attribute we want to maximise/minimise from the OutputModel

            if self._is_better_score(score, best_score, optimisation_config.objective):
                best_score = score
                best_params = params

            iterations += 1
            if (
                optimisation_config.early_stopping
                and iterations >= optimisation_config.max_iterations
            ):
                break

        return best_params, best_score

    def _generate_param_combinations(self, grid):
        """Generate all combinations of parameters from the grid."""
        keys, values = zip(*grid.items())
        for combination in itertools.product(*values):
            yield dict(zip(keys, combination))

    def _apply_params(self, params):
        """Apply parameters to the strategy or configuration."""
        # This needs specific rules and logic to
        # set the required params to the current module
        self.config_manager.update_with_params(params)

    def _is_better_score(self, score, best_score, objective):
        """Compare scores based on the optimization objective."""
        # maybe we want to use a conditional and attribute e.g. "MAXIMISE" "RETURNS"
        if objective == "maximize_returns":
            return score > best_score
        elif objective == "minimize_drawdown":
            return score < best_score
        return False

    def _manage_open_trades(self, data: MarketModel, date: date):
        """Manage open trades."""
        live_trades = self.backtester_trades.get_live_trades()
        for trade in live_trades:
            signal = self._evaluate_close_signals(data=data, date=date, trade=trade)
            if signal:
                self.close_trade(date=date, trade=trade, signal=signal)
            if self._roll_logic():
                self.close_trade(date=date, trade=trade, signal=signal)

    def _roll_logic(self):
        """Logic to control if rolling should take place."""
        # stream_config = self.config_manager.get_config("stream_management")
        # if stream_config and trade.stream_id:
        #     return self._check_stream_roll(trade)
        # return False

    def _evaluate_close_signals(
        self, data: MarketModel, date: date, trade: Trades
    ) -> TradeRule | bool:
        """Evaluate close signals."""
        open_trade_rule = trade.message[0].trade_rule
        relevant_rule = next(
            trade_rule_setting
            for trade_rule_setting in self.strategy_input.trade_rule_settings
            if trade_rule_setting.open_rules == [open_trade_rule]
        )
        for signal in (
            relevant_rule.close_rules
            + relevant_rule.stoploss_rules
            + relevant_rule.takeprofit_rules
        ):
            if signal.evaluate(
                snapshot=data,
                date=date,
                trade=trade,
                trade_schedule=self.backtester_trades,
            ):
                return signal
        return False

    def _evaluate_new_trades(self, data: MarketModel, date: date):
        """Evaluate new trade positions."""
        for trade_rule_setting in self.strategy_input.trade_rule_settings:
            for trade_execution_rule in trade_rule_setting.execution_rules:
                for signal in trade_rule_setting.open_rules:
                    if signal.evaluate(
                        snapshot=data,
                        date=date,
                        trade=trade_execution_rule.trades[0],  # unsure about this
                        trade_schedule=self.backtester_trades,
                    ):
                        self.open_trade(
                            data=data,
                            date=date,
                            trade_rule=signal,
                            trade_execution_rule=trade_execution_rule,
                        )

    def open_trade(
        self,
        data: MarketModel,
        date: date,
        trade_rule: TradeRule,
        trade_execution_rule: ExecutionRule,
    ):
        """Open trade and append to trade schedule."""
        self.backtester_trades.trades.extend(
            trade_execution_rule.execute(
                trade_rule=trade_rule,
                data=data,
                date=date,
            )
        )

    def close_trade(self, date: date, trade: Trades, signal: TradeRule):
        """Close trade."""
        trade.value_date = date
        trade.message.append(TradeMessageModel(date=date, message=signal.rule_type))
