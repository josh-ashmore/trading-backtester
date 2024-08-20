"""Account Model."""

from typing import TYPE_CHECKING
from pydantic import BaseModel, model_validator

from static_data.underlying_data import Currencies

if TYPE_CHECKING:
    from models.rules.execution import Trades


class Account(BaseModel):
    """Account."""

    currency: Currencies
    initial_balance: float
    cash_balance: float = 0

    @model_validator(mode="after")
    def post_validate_cash_balance(self):
        """Post validate cash balance."""
        self.cash_balance = self.initial_balance
        return self

    def update_balance_for_open_trade(self, trade: "Trades"):
        """Update account balance when a trade is opened."""
        self.cash_balance -= trade.notional_amount

    def update_balance_for_close_trade(self, trade: "Trades"):
        """Update account balance when a trade is closed."""
        match trade.instrument_type:
            case "Treasury Bill":
                self.cash_balance += trade.notional_amount
                self.cash_balance *= 1 + (trade.interest_rate) * (
                    (trade.value_date - trade.trade_date).days / 365
                )
            case _:
                pnl = trade.calculate_pnl()
                self.cash_balance += trade.notional_amount + pnl
