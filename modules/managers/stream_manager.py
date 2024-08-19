"""Stream Manager Module."""

from copy import deepcopy
from pydantic import BaseModel, Field, model_validator
from datetime import date
from typing import List, Optional
from dateutil.relativedelta import relativedelta

from models.configs.stream_config import RollInterval, StreamConfig
from models.rules.execution import Trades


class Stream(BaseModel):
    """Stream Model representing a collection of trades managed together."""

    open_date: date = Field(..., description="The date when the stream was opened.")
    close_date: Optional[date] = Field(
        default=None, description="The date when the stream was closed."
    )
    trades: List[Trades] = Field(
        default=[], description="List of trades associated with this stream."
    )

    def generate_trades(
        self, current_date: date, trades_to_open: List[Trades], expiry_date: date
    ):
        """Generate and add trades to the stream based on strategy parameters."""
        for trade in trades_to_open:
            trade.trade_date = current_date
            trade.value_date = expiry_date
            self.trades.extend([trade])

    def roll(self, current_date: date, trades_to_open: List[Trades], expiry_date: date):
        """Roll the stream by closing current trades and generating new ones."""
        self.close_date = current_date
        new_stream = Stream(open_date=current_date)
        new_stream.generate_trades(
            current_date=current_date,
            trades_to_open=trades_to_open,
            expiry_date=expiry_date,
        )
        return new_stream


class StreamManager(BaseModel):
    """Manager for handling multiple streams."""

    stream_config: StreamConfig = Field(..., description="Stream config input.")
    streams: List[Stream] = Field(default=[], description="List of all active streams.")
    trades_to_open: List[Trades] = Field(
        default=[], description="List of trades to be executed within each stream."
    )
    start_date: date

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        self.initialise_streams()
        return self

    def initialise_streams(self):
        """Initialise streams."""
        offset = None
        match self.stream_config.roll_interval:
            case RollInterval.QUARTERLY:
                offset = relativedelta(months=3)
            case RollInterval.MONTHLY:
                offset = relativedelta(months=1)
            case RollInterval.WEEKLY:
                offset = relativedelta(weeks=1)
            case RollInterval.DAILY:
                offset = relativedelta(days=1)
        iterate_dates = [
            self.start_date + offset * i for i in range(self.stream_config.num_streams)
        ]
        for trade_date in iterate_dates:
            stream = Stream(open_date=trade_date)
            stream.generate_trades(
                current_date=trade_date,
                trades_to_open=deepcopy(self.trades_to_open),
                expiry_date=self.calculate_expiry_date(trade_date=trade_date),
            )
            self.streams.append(stream)

    def open_initial_stream(self, open_date: date):
        """Open the initial stream if the strategy start date is not on an expiry."""
        initial_stream = Stream(open_date=open_date)
        initial_stream.generate_trades(
            current_date=open_date,
            trades_to_open=self.trades_to_open,
            expiry_date=self.calculate_expiry_date(trade_date=open_date),
        )
        self.streams.append(initial_stream)

    def roll_streams(self, current_date: date):
        """Roll all streams that are due for rolling."""
        for stream in self.streams:
            if self._is_time_to_roll(stream=stream, current_date=current_date):
                new_stream = stream.roll(
                    current_date=current_date,
                    trades_to_open=self.trades_to_open,
                    expiry_date=self.calculate_expiry_date(trade_date=current_date),
                )
                self.streams.append(new_stream)

    def close_expired_streams(self, current_date: date):
        """Close streams whose trades have reached expiry."""
        for stream in self.streams:
            for trade in stream.trades:
                if trade.value_date == current_date:
                    stream.close_date = current_date
                    # Add any additional logic for closing trades here
                    break

    def _is_time_to_roll(self, stream: Stream, current_date: date) -> bool:
        """Determine if it's time to roll a stream based on the roll interval."""
        # Implement your roll interval logic here, e.g., monthly, quarterly, etc.
        match self.stream_config.roll_interval:
            case RollInterval.MONTHLY:
                return current_date.month != stream.open_date.month
            case RollInterval.DAILY:
                return current_date.day != stream.open_date.day
        return False

    def calculate_expiry_date(self, trade_date: date):
        """Calculate expiry date."""
        return trade_date + relativedelta(
            months=self.stream_config.expiration_interval_months
        )
