"""Test Trade Rules."""

from models.rules.comparison import ComparisonField
from models.rules.rules import TradeCondition, TradeRule


def test_trade_rules():
    """Test Trade Rule Instantiation."""

    trade_rule = TradeRule(
        rule_type="open",
        conditions=[
            TradeCondition(
                evaluate_field=ComparisonField(
                    field="SPX Index",
                    field_type="market_data",
                ),
                comparison_field=ComparisonField(value=100),
                type="greater_than",
            ),
            TradeCondition(
                evaluate_field=ComparisonField(
                    field="Slow Moving Average",
                    field_type="signal_data",
                ),
                comparison_field=ComparisonField(
                    field="Fast Moving Average", field_type="signal_data"
                ),
                type="less_than",
            ),
        ],
        condition_logic_type="AND",
        # execution=[TradeExecution(trades=[])],
    )
    assert trade_rule

    trade_rule_input = {
        "rule_type": "open",
        "conditions": [
            {
                "evaluate_field": {"field": "SPX Index", "field_type": "market_data"},
                "comparison_field": {"value": 100},
                "type": "greater_than",
            },
            {
                "evaluate_field": {
                    "field": "Slow Moving Average",
                    "field_type": "signal_data",
                },
                "comparison_field": {
                    "field": "Fast Moving Average",
                    "field_type": "signal_data",
                },
                "type": "less_than",
            },
        ],
        "condition_logic_type": "AND",
    }
    trade_rule_serialised = TradeRule(**trade_rule_input)
    assert trade_rule_serialised

    assert trade_rule == trade_rule_serialised
