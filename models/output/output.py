"""Backtester Output Models."""

from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel
import numpy as np
from datetime import date, timedelta


from models.trades.schedule import TradeSchedule

if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel


class BacktesterOutput(BaseModel):
    """Backtester Output Model."""

    payoff: Optional[dict[str, list]] = None
    mtm: Optional[dict[str, list]] = None
    premiums_over_time: Optional[dict[str, list]] = None
    slippage_over_time: Optional[dict[str, list]] = None
    live_notional_over_time: Optional[dict[str, list]] = None
    first_strike_over_time: Optional[dict[str, list]] = None
    slippage_over_time_non_cumulative: Optional[dict[str, list]] = None
    restrike_signal_over_time: Optional[dict[str, list]] = None
    pnl: Optional[dict[str, list]] = None
    value: Optional[dict[str, list]] = None
    slippage: Optional[dict[str, list]] = None
    restrike_signal_over_time: Optional[dict[str, list]] = None

    live_pnl: float = 0

    def _calculate(
        self,
        snapshot: "MarketModel",
        dates: list[date],
        trades: TradeSchedule,
        output_currency: str,
    ):
        """Calculate outputs."""
        self.live_trades_dict = {d: [] for d in dates}
        for t in trades:
            day1 = t.trade_date

            day2 = t.value_date if t.__open__ else t.extra_info.close_date
            for d in unpack_dates(min_date=day1 + timedelta(days=1), max_date=day2):
                if d in dates:
                    self.live_trades_dict[d].append(t)

        self.payoff = trades.payoff_over_time(
            data=snapshot, ccy=output_currency, dates=dates
        )

        self.mtm = trades.mtm(data=snapshot, ccy=output_currency, dates=dates)

        self.premiums_over_time = trades.premiums_over_time(
            data=snapshot, ccy=output_currency, dates=dates
        )

        self.slippage_over_time = trades.slippage_over_time(
            data=snapshot, ccy=output_currency, dates=dates
        )

        self.live_notional_over_time = trades.live_notional_over_time(dates=dates)
        self.first_strike_over_time = trades.first_strike_over_time(dates=dates)

        self.slippage_over_time_non_cumulative = trades.slippage_over_time(
            data=snapshot,
            ccy=output_currency,
            dates=dates,
            cumulative=False,
        )

        self.restrike_signal_over_time = trades.restrike_signal_over_time(
            data=snapshot, ccy=output_currency, dates=dates
        )

        self.pnl = {
            "dates": dates,
            "pnl": np.array(self.payoff["payoff"])
            + np.array(self.premiums_over_time["premium"]),
        }
        self.value = {
            "dates": dates,
            "value": np.array(self.payoff["payoff"])
            + self.mtm[0, :]
            + np.array(self.premiums_over_time["premium"]),
        }

        self.slippage = {
            "dates": dates,
            "slippage": np.array(self.slippage_over_time["slippage"]),
        }

        self.restrike_signal_over_time = {
            "dates": dates,
            "restrike_signal": np.array(self.restrike_signal_over_time["restrike"]),
        }
