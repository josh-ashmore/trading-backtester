"""Trade Data Settings Model."""

from typing import Any, Optional
from pydantic import BaseModel, model_validator


class TradeDataSettings(BaseModel):
    """Trade Data Settings Model."""

    base_trade: Optional[dict[str, Any]] = None

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if not self.base_trade:
            self.base_trade = {
                "trade_date": None,
                "value_date": None,
                "delivery_date": None,
                "premium_payment_date": None,
                "moneyness": 1,
                "direction": "Sell",
                "historical": False,
                "dummy_curve": True,
                "premium": 0,
                "Restrike": False,  # would like to rename to lower
            }
        return self
