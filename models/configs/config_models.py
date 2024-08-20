"""Config Models."""

from typing import Annotated, Union

from pydantic import Field
from models.configs.market_data_config import MarketDataConfig
from models.configs.execution_config import ExecutionConfig
from models.configs.portfolio_config import PortfolioConfig
from models.configs.risk_management_config import RiskManagementConfig
from models.configs.optimisation_config import OptimisationConfig
from models.configs.stream_config import StreamConfig

Configs = Annotated[
    Union[
        MarketDataConfig,
        ExecutionConfig,
        PortfolioConfig,
        RiskManagementConfig,
        OptimisationConfig,
        StreamConfig,
    ],
    Field(..., discriminator="config_name"),
]
