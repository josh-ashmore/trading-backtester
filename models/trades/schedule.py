"""Trade Schedule Models."""

from typing import TYPE_CHECKING
from pydantic import BaseModel

from models.rules.enums import ActionType


if TYPE_CHECKING:
    from models.trades.trades import Trades


class TradeSchedule(BaseModel):
    """Trade Schedule Model."""

    trades: list["Trades"]

    def get_live_trades(self):
        """Get live trades."""
        if self.trades == []:
            return []
        return [
            trade
            for trade in self.trades
            if trade.message[-1].message == ActionType.OPEN
        ]
