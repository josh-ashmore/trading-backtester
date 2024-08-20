"""Test Risk Management Config."""

from models.configs.risk_management_config import RiskManagementConfig


def test_risk_management_config():
    """Test risk management config."""

    assert RiskManagementConfig(max_position_size=0.05)
    assert RiskManagementConfig(max_drawdown=0.1)
    assert RiskManagementConfig(stop_loss_pct=0.05)
    assert RiskManagementConfig(position_sizing=0.75)
