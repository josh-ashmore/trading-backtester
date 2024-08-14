"""Account Model."""

from pydantic import BaseModel, model_validator

from static_data.underlying_data import Currencies


class Account(BaseModel):
    """Account."""

    currency: Currencies
    initial_balance: float
    current_balance: float = 0

    @model_validator(mode="after")
    def post_validate_current_balance(self):
        """Post validate current balance."""
        self.current_balance = self.initial_balance
        return self
