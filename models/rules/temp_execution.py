"""Anoter attempt at execution rules."""

from copy import deepcopy
from datetime import date
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field
from typing import Annotated, List, Literal, Optional, Union, TYPE_CHECKING

from models.market_data.cm_models import CMVolatilitySurfaceData
from models.market_data.eq_models import EQVolatilitySurfaceData
from models.market_data.fx_models import FXVolatilitySurfaceData
from models.rules.enums import ActionType
from models.rules.rules import TradeRule
from static_data.underlying_data import AssetClass


if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel


class DirectionType(str, Enum):
    """Direction Type Enum."""

    BUY = "Buy"
    SELL = "Sell"


class CalcualtionType(str, Enum):
    """Calculation Type Enum."""

    PERCENT_OTM = "percent_otm"
    PERCENT_ITM = "percent_itm"
    PERCENT_ATM = "percent_atm"
    DELTA_NEUTRAL = "delta_neutral"
    ABS = "abs"


InstrumentTypes = Literal["Put", "Call", "Future", "Spot", "Treasury Bill"]


class ExecutionRuleType(str, Enum):
    """Execution Rule Enum."""

    BUY = "Buy"
    SELL = "Sell"
    SPREAD = "Spread"


class TradeMessageModel(BaseModel):
    """Trade Message Model."""

    date: date
    message: ActionType
    trade_rule: Optional[TradeRule] = Field(
        default=None, description="Attach the trade rule used to execute this trade."
    )


class BookingModel(BaseModel):
    """Trade Booking Model."""

    trade_date: Optional[date] = None
    value_date: Optional[date] = None
    message: List[TradeMessageModel] = []


class Trade(BookingModel):
    """Base Trade Object."""

    underlying: str
    direction: DirectionType
    instrument_type: InstrumentTypes
    asset_class: AssetClass


class TreasuryBillTrade(Trade):
    """Treasury Bill Trade."""

    instrument_type: Literal["Treasury Bill"] = "Treasury Bill"
    asset_class: AssetClass = AssetClass.FI
    interest_rate: Optional[float] = None


class PutTrade(Trade):
    """Put Trade."""

    premium: float = 0
    instrument_type: Literal["Put"] = "Put"
    strike: Optional[Union[float, int]] = None
    strike_calculation: CalcualtionType = CalcualtionType.ABS


class CallTrade(Trade):
    """Call Trade."""

    premium: float = 0
    instrument_type: Literal["Call"] = "Call"
    strike: Optional[Union[float, int]] = None
    strike_calculation: CalcualtionType = CalcualtionType.ABS


Trades = Annotated[
    Union[CallTrade, PutTrade, TreasuryBillTrade],
    Field(..., discriminator="instrument_type"),
]


class ExecutionRule(BaseModel):
    """Execution Rule Model."""

    rule_type: ExecutionRuleType
    trades: List[Trades]

    current_cost: Optional[float | None] = None
    target_cost: Optional[float | None] = None

    def execute(self, trade_rule: TradeRule, data: "MarketModel", date: date):
        """Execute all trades logic."""
        new_trades = []
        match self.rule_type:
            case ExecutionRuleType.SPREAD:
                total_cost = 0
                self.current_cost = total_cost
                for trade in deepcopy(self.trades):
                    new_trades.append(
                        self.execute_trade(
                            trade=trade, data=data, date=date, trade_rule=trade_rule
                        )
                    )
                    total_cost += trade.premium
                    self.current_cost = total_cost

                if (
                    self.target_cost  # leaving this so we can check trade results
                    # isinstance(self.target_cost, float | int)
                    and abs(total_cost - self.target_cost) >= 0.01
                ):
                    return []
            case ExecutionRuleType.BUY | ExecutionRuleType.SELL:
                for trade in deepcopy(self.trades):
                    new_trades.append(
                        self.execute_trade(
                            trade=trade, data=data, date=date, trade_rule=trade_rule
                        )
                    )
        return new_trades

    def execute_trade(
        self, trade: Trades, data: "MarketModel", date: date, trade_rule: TradeRule
    ):
        """Execute each trade logic."""
        trade.trade_date = date
        match trade.instrument_type:
            case "Call" | "Put":
                return self._execute_option_trade(trade, data, date, trade_rule)
            case "Treasury Bill":
                return self._execute_treasury_bill_trade(trade, data, date, trade_rule)
            case _:
                raise ValueError(f"Unknown trade type: {trade.instrument_type}")

    def _execute_option_trade(
        self,
        trade: PutTrade | CallTrade,
        data: "MarketModel",
        date: date,
        trade_rule: TradeRule,
    ):
        """Execute option trade logic."""
        vol_surf: (
            FXVolatilitySurfaceData | EQVolatilitySurfaceData | CMVolatilitySurfaceData
        ) = [
            datum
            for datum in getattr(data, trade.asset_class)[trade.underlying].volatility
            if datum.spot_date == date
        ][
            0
        ]
        trade.value_date = next(
            datum.maturity for datum in vol_surf.surface if datum.maturity >= date
        )
        trade.strike = self.calculate_strike_price(
            data=data,
            trade=trade,
            date=date,
            current_cost=self.current_cost,
            tolerance=1e-4,
        )
        option_price = data.get(
            market_variable="Option Price",
            underlying=trade.underlying,
            date=date,
            maturity_date=trade.value_date,
            asset_class=trade.asset_class,
            strike=trade.strike,
            instrument_type=trade.instrument_type,
        )

        match trade.direction:
            case DirectionType.BUY:
                trade_premium = -option_price
            case DirectionType.SELL:
                trade_premium = option_price

        trade.premium = trade_premium
        trade.message.append(
            TradeMessageModel(date=date, message=ActionType.OPEN, trade_rule=trade_rule)
        )
        return trade

    def _execute_treasury_bill_trade(
        self,
        trade: TreasuryBillTrade,
        data: "MarketModel",
        date: date,
        trade_rule: TradeRule,
    ):
        """Execute Treasury Bill Trade."""
        yield_curve = next(
            curve for curve in data.FI["US10Y"].yield_curve if curve.spot_date == date
        )
        next_maturity_date = next(
            date for date in yield_curve.maturity_dates if date >= date
        )
        trade.interest_rate = yield_curve.yields[
            yield_curve.maturity_dates.index(next_maturity_date)
        ]
        trade.message.append(
            TradeMessageModel(date=date, message=ActionType.OPEN, trade_rule=trade_rule)
        )
        return trade

    def calculate_strike_price(
        self,
        data: "MarketModel",
        trade: Trades,
        date: date,
        current_cost: Optional[float] = None,
        tolerance: float = 1e-4,
    ):
        """Calculate strike price based on combined type."""
        strike = (
            self.calculate_dynamic_strike(
                data=data,
                date=date,
                trade=trade,
                current_cost=current_cost,
                tolerance=tolerance,
            )
            if trade.strike is None
            else trade.strike
        )

        match trade.strike_calculation:
            case CalcualtionType.PERCENT_OTM:
                return data.get(
                    market_variable="Spot",
                    underlying=trade.underlying,
                    date=date,
                    asset_class=trade.asset_class,
                ) * (1 - strike / 100)
            case CalcualtionType.PERCENT_ITM:
                return data.get(
                    market_variable="Spot",
                    underlying=trade.underlying,
                    date=date,
                    asset_class=trade.asset_class,
                ) * (1 + strike / 100)
            case CalcualtionType.PERCENT_ATM:
                return data.get(
                    market_variable="Spot",
                    underlying=trade.underlying,
                    date=date,
                    asset_class=trade.asset_class,
                )
            case CalcualtionType.DELTA_NEUTRAL:
                return self.calculate_delta_neutral_strike(
                    data=data, date=date, trade=trade
                )
            case CalcualtionType.ABS:
                return strike
            case _:
                raise ValueError("Invalid strike calculation type")

    def calculate_delta_neutral_strike(
        self, data: "MarketModel", date: date, trade: Trade
    ):
        # Implement your delta-neutral strike calculation logic here.
        # This might involve complex calculations with option Greeks.
        # For demonstration, assume it to be ATM (asset price):
        return data.get(
            market_variable="Spot",
            underlying=trade.underlying,
            date=date,
            asset_class=trade.asset_class,
        )  # Simplified for demonstration purposes

    def calculate_dynamic_strike(
        self,
        data: "MarketModel",
        trade: Trade,
        date: date,
        current_cost: float,
        tolerance: float = 1e-4,
    ):
        """Dynamically calculate the strike for an option.

        The aim is to achieve target cost using bisection method.
        """
        remaining_cost = self.target_cost - current_cost

        # Define the boundaries for strike price, for demonstration using a percentage
        #   range
        asset_price = data.get(
            market_variable="Spot",
            underlying=trade.underlying,
            date=date,
            asset_class=trade.asset_class,
        )
        low_strike = asset_price * 0.5  # 50% of the asset price as lower bound
        high_strike = asset_price * 1.5  # 150% of the asset price as upper bound

        def cost_difference(strike: float, data: "MarketModel", date: date):
            """Cost difference.

            Define a function to find the root of
            (this function should be zero at the correct strike).
            """
            option_price = data.get(
                market_variable="Option Price",
                underlying=trade.underlying,
                date=date,
                maturity_date=trade.value_date,
                asset_class=trade.asset_class,
                strike=strike,
                instrument_type=trade.instrument_type,
            )
            return option_price + remaining_cost

        # Implement the bisection method
        while high_strike - low_strike > tolerance:
            mid_strike = (low_strike + high_strike) / 2
            mid_cost_diff = cost_difference(strike=mid_strike, data=data, date=date)

            if np.abs(mid_cost_diff) < tolerance:
                return mid_strike

            if mid_cost_diff > 0:
                low_strike = mid_strike
            else:
                high_strike = mid_strike

        return (low_strike + high_strike) / 2
