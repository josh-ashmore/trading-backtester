"""Risk Management Config."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class RiskManagementConfig(BaseModel):
    """Risk Management Config Model.

    This config handles risk parameters like
    position sizing, stop-loss levels, and risk limits.
    """

    config_name: Literal["risk_management"] = Field(
        default="risk_management",
        description="Name of the risk management configuration.",
    )
    max_drawdown: Optional[float] = Field(
        default=None,
        description="Maximum drawdown percentage before closing all positions.",
    )
    stop_loss_pct: Optional[float] = Field(
        default=None, description="Stop loss level as a percentage of position size."
    )
    position_sizing: Optional[float] = Field(
        default=None,
        description="Maximum allowable position size as a percentage of portfolio.",
    )
    portfolio_limit: Optional[float] = Field(
        default=None, description="Maximum allowable portfolio exposure."
    )
