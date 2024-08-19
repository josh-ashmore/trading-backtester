"""Backtest Execution Rules."""

import numpy as np
from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Literal, Optional, Dict, Any


from models.trades.spot_trade import Trades

if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel


Direction = Literal["Buy", "Sell"]


class OrderType(str, Enum):
    """Order Type Enum."""

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    PARTIALLY_FILLED = "partially_filled"


class TradeDetails(BaseModel):
    underlying: str
    direction: Direction
    style: str
    notional_amounts: float | None = None  # fill this in later
    price: Optional[float] = None
    order_type: OrderType = OrderType.MARKET
    timestamp: datetime = Field(default_factory=datetime.now)  # timezone.utc

    premium_payment_date: date | None = None

    # unsure
    relative_pos: int
    slip_rate: tuple[str, float] = ("dollar_abs", 0)
    adjust_notional_factor: str = "Strike"
    moneyness: float = 1.00

    # Optional fields for limit/stop orders
    stop_price: Optional[float] = None  # For stop-loss or take-profit orders
    limit_price: Optional[float] = None  # For limit orders

    def execute_trade(self, snapshot: "MarketModel", date: date) -> Dict[str, Any]:
        """Execute the trade based on current market conditions."""
        # Placeholder logic; actual implementation depends on how you simulate trades
        current_value = snapshot.get(f"{self.underlying} Spot", dates=date)

        if self.order_type == OrderType.MARKET:
            executed_price = current_value
        elif self.order_type == OrderType.LIMIT and current_value <= self.limit_price:
            executed_price = current_value
        elif (
            self.order_type == OrderType.STOP_LOSS and current_value <= self.stop_price
        ):
            executed_price = self.stop_price
        else:
            executed_price = None

        return {
            "underlying": self.underlying,
            "direction": self.direction,
            # "notional_amounts": self.notional_amounts,
            "strike": executed_price,
            "timestamp": self.timestamp,
            "status": "filled" if executed_price else "unfilled",
        }


class TradeExecution(BaseModel):
    """Trade Execution Model."""

    trade_details: List[TradeDetails]
    model_type: str

    REQUIRED_SIGNALS: list[str] | None = None

    def validate_required_signals(self, snapshot: "MarketModel"):
        """Validate required signals."""
        if self.REQUIRED_SIGNALS is not None:
            for signal in self.REQUIRED_SIGNALS:
                assert signal in snapshot.variable_names
        return self

    def slippage_adjustment(
        self,
        trade: "Trades",
        leg: Any,
        snapshot: "MarketModel",
        account_slippage_: bool = True,
        notional_adjustment: bool = False,
    ):
        """Incorporates transaction cost when opening or closing a trade.


        Args:
            trade (Trade): trade at which transaction cost is included in
            leg (Leg): leg of trade where trade info is extracted.
            premium (bool, optional): to adjust account based on trade premium.
                Defaults to True
            slippage_ (bool, optional): to adjust account based on slippage.
                Defaults to True
        """
        slip_rate: str = trade.slip_rate[0]
        match slip_rate:
            case "dollar_abs":
                slippage = -1 * trade.slip_rate[-1]
            case "premium_pct":
                slippage = -1 * np.abs(trade.legs[-1].premium * trade.slip_rate[-1])
            case "notional_pct":
                slippage = -1 * trade.slip_rate[-1] * trade.legs[-1].notional_in_ccy
            case "dollar_notional_abs":
                slippage = self._dollar_notional_abs_slippage(
                    trade=trade, leg=leg, snapshot=snapshot
                )
            case _:
                slippage = 0

        leg.slippage = 0
        if account_slippage_:
            leg.slippage = slippage
            self.account.access(
                data=snapshot,
                notional=slippage,
                ccy=self.base_trade["premium_currency"],
                date=leg.trade_date,
                for_ccy=True,
            )
        if notional_adjustment:
            trade.legs[0].notional_amounts = trade.legs[0].notional_amounts + slippage
        return slippage

    def _dollar_notional_abs_slippage(
        self, trade: "Trades", leg: Any, snapshot: "MarketModel"
    ):
        """Calculate slippage with dollar_notional_abs slip rate style."""
        adjust_notional_factor = trade.adjust_notional_factor
        match adjust_notional_factor:
            case "Spot":
                if trade.premium_payment_date == leg.premium_payment_date:
                    factor = snapshot.get(
                        trade.underlying + " Spot",
                        dates=leg.premium_payment_date,
                    )[0][0]
                else:
                    factor = trade.spot_ref[0][0]
            case "Strike":
                value_date = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).expiry_dates[trade.legs[0].relative_pos]
                style_ = "Put" if "Put" in trade.style else "Call"
                factor = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).strike(
                    style=style_,
                    pos_pair=("expiry_date", value_date),
                    moneyness_pair=("moneyness", trade.moneyness),
                )
            case "Synthetic_long":
                value_date = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).expiry_dates[trade.legs[0].relative_pos]
                tenor = ("expiry_date", value_date)
                strike = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).strike(
                    style="Put",
                    pos_pair=("expiry_date", value_date),
                    moneyness_pair=("moneyness", trade.moneyness),
                )
                call_premium_price = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).price(
                    style="Call",
                    pos_pair=tenor,
                    moneyness_pair=("strike", strike),
                )
                put_premium_price = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).price(
                    style="Put",
                    pos_pair=tenor,
                    moneyness_pair=("strike", strike),
                )
                factor = strike - put_premium_price + call_premium_price
            case "Strike_premium":
                value_date = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).expiry_dates[trade.legs[0].relative_pos]
                tenor = ("expiry_date", value_date)
                strike = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).strike(
                    style="Put",
                    pos_pair=("expiry_date", value_date),
                    moneyness_pair=("moneyness", trade.moneyness),
                )
                put_premium_price = snapshot.get(
                    f"{trade.underlying} EXSurface", dates=trade.trade_date
                ).price(
                    style="Put",
                    pos_pair=tenor,
                    moneyness_pair=("strike", strike),
                )

                factor = strike - put_premium_price
        return -1 * trade.slip_rate[-1] * trade.legs[-1].notional_amounts / factor

    def calculate_notional(self, trade_details: TradeDetails, date: date, **kwargs):
        """Calculate notional of trade."""
        raise NotImplementedError("Not implemented yet.")

    def calculate_moneyness(self, date: date, **kwargs):
        """Calculate moneyness of trade."""
        raise NotImplementedError("Not implemented yet.")


# class GLDOverlayExecution(TradeExecution):
#     """GLD Overlay Execution Model."""

#     leverage_ratio: float | int | str = 1
#     percent_allocation: float = 0.2
#     model_type: str = "GLDOverlay"

#     REQUIRED_SIGNALS: list[str] = [
#         "VIX GVZ 22D Ratio SIGNAL",
#         "GLD Call Imp Vol SIGNAL",
#     ]

#     def calculate_notional(
#         self,
#         trade_details: TradeDetails,
#         date: date,
#         snapshot: "MarketModel",
#         account: Any,
#         live_trades_set: dict[str, set["Trades"]],
#     ):
#         """Calculate notional of trade."""

#         total_opt_mtm = 0
#         total_open_notional = 0

#         for _, set_trades in live_trades_set.items():
#             total_set_opt_mtm = sum(
#                 trade.mtm(data=snapshot, dates=date) for trade in set_trades
#             )
#             total_set_open_notional = sum(
#                 trade.legs[0].strike * trade.legs[0].notional_amounts
#                 for trade in set_trades
#                 if "Option" in trade.style
#             )
#             total_opt_mtm += total_set_opt_mtm
#             total_open_notional += total_set_open_notional
#         balance_account = account.balance
#         if not isinstance(self.leverage_ratio, (int, float)):
#             assert self.leverage_ratio == "dynamic"
#             self.leverage_ratio = snapshot.get("VIX GVZ 22D Ratio SIGNAL", dates=date)[
#                 0
#             ][0]
#             self.leverage_ratio = max(1, self.leverage_ratio)
#         max_spend = self.leverage_ratio * balance_account
#         first_term = self.percent_allocation * (max_spend + total_opt_mtm)
#         second_term = max_spend - total_open_notional
#         allocation = max(0, min(first_term, second_term))

#         match trade_details.style:
#             case "ExchangeSpot":
#                 return allocation * self.is_over_min_iv(snapshot=snapshot, date=date)
#             case "ExchangePutOption":
#                 return allocation * (
#                     1 - self.is_over_min_iv(snapshot=snapshot, date=date)
#                 )

#     def is_over_min_iv(
#         self,
#         snapshot: "MarketModel",
#         date: date,
#         linear_range: tuple[int, int] = (10, 10),
#     ):
#         iv = snapshot.get("GLD Call Imp Vol SIGNAL", dates=date)[0][0]
#         if iv <= linear_range[0]:
#             return 0.0
#         elif iv > linear_range[1]:
#             return 1.0
#         else:
#             dy, dx = 1, linear_range[1] - linear_range[0]
#             return (dy / dx) * (iv - linear_range[0])

#     def calculate_moneyness(self, snapshot: "MarketModel", date: date):
#         """Calculate moneyness of trade."""
#         implied_volatility = snapshot.get("GLD Call Imp Vol SIGNAL", dates=date)[0][0]
#         if implied_volatility < 30:
#             return 1.015
#         elif implied_volatility > 50:
#             return 1.2
#         else:
#             return 1.015 + (0.185 / 20) * (implied_volatility - 30)  # Linear
