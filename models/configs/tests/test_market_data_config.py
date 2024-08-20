"""Test Market Data Config."""

from copy import deepcopy
from models.configs.market_data_config import (
    DataSource,
    MarketDataConfig,
    SubTransformation,
    Transformation,
)


def test_market_data_config(market_data):
    """Test market data config."""

    market_data_config = MarketDataConfig(
        transformations=[
            Transformation(
                data_source=DataSource(
                    underlying="GOLD", market_variable_name="spot", asset_class="CM"
                ),
                sub_transformations=[
                    SubTransformation(frequency="day", transformation_type="log_return")
                ],
            )
        ]
    )

    market_data_config.apply_transformations(market_data=deepcopy(market_data))

    assert market_data_config
