"""Market Model."""

from datetime import date
from enum import Enum
from typing import Dict, Optional, Union
from pydantic import BaseModel

from models.market_data.cc_models import CCMarketData
from models.market_data.cm_models import CMMarketData
from models.market_data.eq_models import EQMarketData
from models.market_data.fi_models import FIMarketData
from models.market_data.fx_models import FXMarketData
from models.trades.enums import InstrumentTypes
from static_data.underlying_data import AssetClass


class MarketVariables(str, Enum):
    """Market Variables Enum."""

    SPOT = "Spot"
    FUTURE = "Future"
    VOL = "Vol"
    OPTION_PRICE = "Option Price"


class MarketModel(BaseModel):
    """Market Model."""

    FX: Dict[str, FXMarketData] = {}
    EQ: Dict[str, EQMarketData] = {}
    FI: Dict[str, FIMarketData] = {}
    CC: Dict[str, CCMarketData] = {}
    CM: Dict[str, CMMarketData] = {}

    def get(
        self,
        market_variable: MarketVariables,
        asset_class: AssetClass,
        underlying: str,
        date: date,
        maturity_date: Optional[date] = None,
        strike: Optional[float] = None,
        instrument_type: Optional[InstrumentTypes] = None,
    ):
        """Get data."""
        match market_variable:
            case MarketVariables.SPOT:
                return self.get_spot(
                    underlying=underlying, date=date, asset_class=asset_class
                )
            case MarketVariables.FUTURE:
                return True
            case MarketVariables.VOL:
                return True
            case MarketVariables.OPTION_PRICE:
                return self.get_option_price(
                    underlying=underlying,
                    date=date,
                    maturity_date=maturity_date,
                    asset_class=asset_class,
                    strike=strike,
                    instrument_type=instrument_type,
                )
            case _:
                return NotImplementedError(
                    f"Market variable not implemented for {market_variable}"
                )

    def get_spot(self, underlying: str, date: date, asset_class: AssetClass):
        """Get spot rate."""
        data: Dict[
            str,
            Union[
                FXMarketData | FIMarketData | EQMarketData | CMMarketData | CCMarketData
            ],
        ] = getattr(self, asset_class)
        return next(
            datum.price for datum in data[underlying].spot if datum.spot_date == date
        )

    def get_option_price(
        self,
        underlying: str,
        date: date,
        maturity_date: date,
        asset_class: AssetClass,
        strike: float,
        instrument_type: InstrumentTypes,
    ):
        """Get option price."""
        data: Dict[
            str,
            Union[
                FXMarketData | FIMarketData | EQMarketData | CMMarketData | CCMarketData
            ],
        ] = getattr(self, asset_class)
        surface = next(
            surface.surface
            for surface in data[underlying].volatility
            if surface.spot_date == date
        )
        match instrument_type:
            case "Call":
                return next(
                    datum.call_price
                    for datum in surface
                    if datum.strike <= strike and datum.maturity == maturity_date
                )
            case "Put":
                return next(
                    datum.put_price
                    for datum in surface
                    if datum.strike <= strike and datum.maturity == maturity_date
                )

    def get_next_expiry(
        self,
        underlying: str,
        date: date,
        asset_class: AssetClass,
        instrument_type: InstrumentTypes,
    ):
        """Get next expiry date."""
        data: Dict[
            str,
            Union[
                FXMarketData | FIMarketData | EQMarketData | CMMarketData | CCMarketData
            ],
        ] = getattr(self, asset_class)
        surface = next(
            surface.surface
            for surface in data[underlying].volatility
            if surface.spot_date == date
        )
        match instrument_type:
            case "Call":
                return next(
                    datum.maturity for datum in surface if datum.maturity >= date
                )
            case "Put":
                return next(
                    datum.maturity for datum in surface if datum.maturity >= date
                )
