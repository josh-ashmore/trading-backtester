"""Test stream manager module."""

from datetime import date

from models.configs.stream_config import StreamConfig
from models.rules.execution import CallTrade, PutTrade
from models.trades.trades import NotionalRule
from modules.managers.stream_manager import StreamManager

# from modules.tests.stream_expected_outputs import EXPECTED_OUTPUT


def test_stream_manager():
    """Test stream manager."""

    start_date = date(2024, 1, 1)
    stream_manager = StreamManager(
        stream_config=StreamConfig(
            num_streams=12, roll_interval="monthly", expiration_interval=12
        ),
        start_date=start_date,
        trades_to_open=[
            PutTrade(
                underlying="GOLD",
                direction="Buy",
                asset_class="CM",
                notional_rule=NotionalRule(rule_type="fixed", value=1),
            ),
            CallTrade(
                underlying="GOLD",
                direction="Sell",
                asset_class="CM",
                notional_rule=NotionalRule(rule_type="fixed", value=1),
            ),
        ],
    )
    assert stream_manager
