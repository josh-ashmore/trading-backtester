"""Backtester Output Models."""

from typing import List
from pydantic import BaseModel, Field
import numpy as np

from models.account.account import Account
from models.rules.execution import Trades


class BacktesterOutput(BaseModel):
    """Model to calculate and store performance metrics."""

    returns: List[float] = Field(default=[], description="Daily/weekly returns.")
    drawdown: List[float] = Field(default=[], description="Drawdowns over the period.")
    max_drawdown: float = Field(default=0.0, description="Maximum drawdown observed.")
    sharpe_ratio: float = Field(
        default=0.0, description="Sharpe ratio of the strategy."
    )

    def evaluate(
        self, trades: List[Trades], account: Account, risk_free_rate: float = 0
    ):
        """Evaluate all metrics."""
        self.calculate_returns(trades=trades, account=account)
        self.calculate_drawdown()
        self.calculate_sharpe_ratio(risk_free_rate=risk_free_rate)

    def calculate_returns(self, trades: List[Trades], account: Account):
        """Calculate returns based on trade PnL."""
        cumulative_pnl = 0.0

        for trade in trades:
            if trade.close_price is not None:
                pnl = trade.calculate_pnl()
                cumulative_pnl += pnl

                trade_return = cumulative_pnl / account.initial_balance
                self.returns.append(trade_return)

    def calculate_drawdown(self):
        """Calculate drawdown."""
        peak = -float("inf")
        for value in self.returns:
            peak = max(peak, value)
            self.drawdown.append((peak - value) / peak if peak != 0 else 0)
        self.max_drawdown = max(self.drawdown)

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.0):
        """Calculate Sharpe ratio."""
        if self.returns:
            mean_return = np.mean(self.returns)
            return_std = np.std(self.returns)
            self.sharpe_ratio = (
                (mean_return - risk_free_rate) / return_std if return_std != 0 else 0
            )


# class BacktesterOutput(BaseModel):
#     """Backtester Output Model."""

#     payoff: Optional[dict[str, list]] = None
#     mtm: Optional[dict[str, list]] = None
#     premiums_over_time: Optional[dict[str, list]] = None
#     slippage_over_time: Optional[dict[str, list]] = None
#     live_notional_over_time: Optional[dict[str, list]] = None
#     first_strike_over_time: Optional[dict[str, list]] = None
#     slippage_over_time_non_cumulative: Optional[dict[str, list]] = None
#     restrike_signal_over_time: Optional[dict[str, list]] = None
#     pnl: Optional[dict[str, list]] = None
#     value: Optional[dict[str, list]] = None
#     slippage: Optional[dict[str, list]] = None
#     restrike_signal_over_time: Optional[dict[str, list]] = None

#     live_pnl: float = 0

#     def _calculate(
#         self,
#         snapshot: "MarketModel",
#         dates: list[date],
#         trades: TradeSchedule,
#         output_currency: str,
#     ):
#         """Calculate outputs."""
#         self.live_trades_dict = {d: [] for d in dates}
#         for t in trades:
#             day1 = t.trade_date

#             day2 = t.value_date if t.__open__ else t.extra_info.close_date
#             for d in unpack_dates(min_date=day1 + timedelta(days=1), max_date=day2):
#                 if d in dates:
#                     self.live_trades_dict[d].append(t)

#         self.payoff = trades.payoff_over_time(
#             data=snapshot, ccy=output_currency, dates=dates
#         )

#         self.mtm = trades.mtm(data=snapshot, ccy=output_currency, dates=dates)

#         self.premiums_over_time = trades.premiums_over_time(
#             data=snapshot, ccy=output_currency, dates=dates
#         )

#         self.slippage_over_time = trades.slippage_over_time(
#             data=snapshot, ccy=output_currency, dates=dates
#         )

#         self.live_notional_over_time = trades.live_notional_over_time(dates=dates)
#         self.first_strike_over_time = trades.first_strike_over_time(dates=dates)

#         self.slippage_over_time_non_cumulative = trades.slippage_over_time(
#             data=snapshot,
#             ccy=output_currency,
#             dates=dates,
#             cumulative=False,
#         )

#         self.restrike_signal_over_time = trades.restrike_signal_over_time(
#             data=snapshot, ccy=output_currency, dates=dates
#         )

#         self.pnl = {
#             "dates": dates,
#             "pnl": np.array(self.payoff["payoff"])
#             + np.array(self.premiums_over_time["premium"]),
#         }
#         self.value = {
#             "dates": dates,
#             "value": np.array(self.payoff["payoff"])
#             + self.mtm[0, :]
#             + np.array(self.premiums_over_time["premium"]),
#         }

#         self.slippage = {
#             "dates": dates,
#             "slippage": np.array(self.slippage_over_time["slippage"]),
#         }

#         self.restrike_signal_over_time = {
#             "dates": dates,
#             "restrike_signal": np.array(self.restrike_signal_over_time["restrike"]),
#         }
