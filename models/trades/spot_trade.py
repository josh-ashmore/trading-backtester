"""Spot trade."""

from datetime import date
from typing import TYPE_CHECKING, Annotated, ClassVar, Literal, Union
from pydantic import BaseModel, Field


from static_data.underlying_data import AssetClass

if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel


class SpotTrade(BaseModel):
    """Spot Trade."""

    trade_date: date
    value_date: date
    underlying: str

    asset_class: AssetClass

    open: bool = False


class FXTradeHelper(BaseModel):
    """FX Trade Helper Model."""

    strike: float
    notional_amount: float


class FXSpotTrade(SpotTrade, FXTradeHelper):
    """FX Spot Trade."""

    style: Literal["FXSpotTrade"] = Field(
        default="FX Spot Trade", json_schema_extra={"type": "string"}
    )
    asset_class: ClassVar[AssetClass] = AssetClass.FX

    def settlement(self, data: "MarketModel", date: date):
        """Calculate settlement value."""

        return (
            next(
                datum.price
                for datum in data.fx_data[self.underlying].spot
                if datum.spot_date == date
            )
            - self.strike
        ) * self.notional_amount


class EQSpotTrade(SpotTrade):
    """EQ Spot Trade."""

    style: Literal["EQSpotTrade"] = Field(
        default="EQ Spot Trade", json_schema_extra={"type": "string"}
    )
    asset_class: ClassVar[AssetClass] = AssetClass.EQ


Trades = Annotated[
    Union[FXSpotTrade, EQSpotTrade],
    Field(..., discriminator="style"),
]
