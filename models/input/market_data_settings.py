"""Market Data Settings Model."""

from datetime import date, datetime
from typing import Any, Optional
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

from static_data.underlying_data import Currencies, StrategyAssetClasses


class SignalDataModel(BaseModel):
    """Signal Data Model."""

    signal_name: str
    data: list[dict] | pd.DataFrame
    date_key_name: str
    value_key_name: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if not isinstance(self.data, pd.DataFrame):
            self.data = pd.DataFrame(data=self.data)
        return self

    def prepare_signal_data(self, market_data_set_dict: dict[date, Any]):
        """Prepare signal data to be ingested by pricing model."""
        data = self.data[[self.date_key_name, self.value_key_name]].dropna()
        dates = [
            _date
            for _date in data[self.date_key_name].apply(
                lambda x: datetime.strptime(x, "%Y-%m-%d").date()
            )
        ]
        data = dict(zip(dates, data[self.value_key_name]))
        data = {
            date_: data[date_] for date_ in data if date_ in market_data_set_dict.keys()
        }
        return data


class MarketDataSettings(BaseModel):
    """Market Data Settings."""

    spot_date: date
    underlying: str
    currency: Currencies = Field(examples=["USD"])
    pricing_currencies_map: dict[str, str] = Field(examples=[{"USD": "USD OIS"}])
    asset_class: StrategyAssetClasses = Field(examples=["FX", "EQ"])
    signal_data: Optional[list[SignalDataModel]] = None
    underlying_map: Optional[dict[str, str]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        self._set_underlying_map()
        return self

    def _set_underlying_map(self):
        """Set underlying map."""
        self.underlying_map = {
            f"{self.asset_class.lower()}_underlyings": [self.underlying],
        }
