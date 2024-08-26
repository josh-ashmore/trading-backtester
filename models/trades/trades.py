"""Trades."""

from typing import Annotated, Union

from pydantic import Field

from models.trades.trade_models import CallTrade, PutTrade, TreasuryBillTrade


Trades = Annotated[
    Union[CallTrade, PutTrade, TreasuryBillTrade],
    Field(..., discriminator="instrument_type"),
]
