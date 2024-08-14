"""Portfolio Config."""

from enum import Enum
from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field


class RebalancingFrequency(str, Enum):
    """Rebalancing Frequency Enum."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class PortfolioConfig(BaseModel):
    """Portfolio Config Model.

    This config controls the portfolio's overall
    strategy, asset allocation, and rebalancing rules.
    """

    config_name: Literal["portfolio"] = Field(
        default="portfolio", description="Name of the portfolio configuration."
    )
    asset_allocation: Dict[str, float] = Field(
        description="Asset allocation as a percentage of "
        "total portfolio, e.g., {'stocks': 60, 'bonds': 40}."
    )
    rebalancing_frequency: RebalancingFrequency = Field(
        description="How often the portfolio is rebalanced."
    )
    leverage: Optional[float] = Field(
        default=None, description="Leverage level applied to the portfolio."
    )
