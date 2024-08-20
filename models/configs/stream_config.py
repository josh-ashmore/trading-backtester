"""Stream Config."""

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Literal
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from modules.managers.stream_manager import Stream


class RollInterval(str, Enum):
    """Roll Interval Enum."""

    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"


class StreamConfig(BaseModel):
    """Stream Config Model.

    This config controls how streams of trades can be placed and rolled automatically
    without the requirement for duplicating trade and execution rules.
    """

    config_name: Literal["stream"] = Field(
        default="stream", description="Name of the stream configuration."
    )
    num_streams: int = Field(default=12, description="Number of concurrent streams.")
    roll_interval: RollInterval = Field(
        default="monthly", description="Interval at which streams roll."
    )
    expiration_interval_months: int = Field(
        default=12, description="Expiration interval in months for each stream."
    )

    def is_roll_due(self, stream: "Stream", current_date: date):
        """Determine if the stream should be rolled.

        Logic is based on roll_interval and expiration_interval.
        """
        roll_due = False
        if self.roll_interval == RollInterval.MONTHLY:
            roll_due = current_date.month != stream.open_date.month

        # Add other interval checks (e.g., weekly, daily) as needed
        return roll_due
