"""Test open rules."""

from datetime import date
from models.rules.comparison import ComparisonField, DateField, DateSettings
from models.rules.rules import TradeCondition, TradeRule
from models.trades.trade_models import CallTrade


def test_trade_rule(market_data):
    """Test trade rule."""
    trade_rule = TradeRule(
        rule_type="open",
        conditions=[
            TradeCondition(
                comparison_one=ComparisonField(
                    field_settings=DateField(field="expiry"),
                    additional_settings=DateSettings(offset=2, offset_type="expiry"),
                ),
                comparison_two=ComparisonField(
                    field_settings=DateField(field="current")
                ),
                type="equal_to",
            ),
        ],
        condition_logic_type="AND",
    )

    trade = CallTrade(
        underlying="GOLD",
        asset_class="CM",
        direction="Sell",
        notional_rule={"rule_type": "percentage_of_account", "value": 0.5},
    )

    assert trade_rule.conditions[0].comparison_one.return_value(
        date=date(2024, 1, 1),
        data=market_data,
        trade=trade,
    ) == date(2024, 3, 31)
