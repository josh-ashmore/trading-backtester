"""Backtest rules."""

from datetime import date
from pydantic import BaseModel, Field
from typing import TYPE_CHECKING, List, Optional

from models.rules.comparison import ComparisonField
from models.rules.enums import ValueConditionType, ActionType, LogicType
from models.trades.schedule import TradeSchedule
from models.trades.trades import Trades


if TYPE_CHECKING:
    from models.market_data.market_model import MarketModel


class TradeCondition(BaseModel):
    """Trade Condition Model."""

    comparison_one: ComparisonField
    comparison_two: ComparisonField
    type: ValueConditionType = Field(
        description="The type of condition to compare.",
        examples=["greater_than", "equal_to"],
    )

    def evaluate(
        self,
        data: "MarketModel",
        date: date,
        trade: Optional["Trades"] = None,
        trade_schedule: Optional[TradeSchedule] = None,
    ) -> bool:
        """Evaluate if condition is met."""
        comparison_one_value = self.comparison_one.return_value(
            date=date, data=data, trade=trade, trade_schedule=trade_schedule
        )
        comparison_two_value = self.comparison_two.return_value(
            date=date, data=data, trade=trade, trade_schedule=trade_schedule
        )

        match self.type:
            case ValueConditionType.GREATER_THAN:
                return comparison_one_value > comparison_two_value
            case ValueConditionType.LESS_THAN:
                return comparison_one_value < comparison_two_value
            case ValueConditionType.EQUAL_TO:
                return comparison_one_value == comparison_two_value
            case ValueConditionType.GREATER_THAN_EQUAL_TO:
                return comparison_one_value >= comparison_two_value
            case ValueConditionType.LESS_THAN_EQUAL_TO:
                return comparison_one_value <= comparison_two_value
            case ValueConditionType.NOT_EQUAL_TO:
                return comparison_one_value != comparison_two_value
            case ValueConditionType.IN_RANGE:
                assert len(comparison_two_value) > 1
                return comparison_one_value in comparison_two_value
            case ValueConditionType.NOT_IN_RANGE:
                assert len(comparison_two_value) > 1
                return comparison_one_value not in comparison_two_value
        return False


class TradeRule(BaseModel):
    """
    Initializes a trade rule.


    Parameters:
    - rule_type: A string indicating the type of rule (e.g., 'open', 'close').
    - conditions: A list of callables (functions/lambdas) that return a boolean,
        representing individual conditions.
    - logic: A string that defines how to combine conditions ('AND' or 'OR').
    - action: A callable that defines what action to take if the rule is triggered.
        Defaults to a simple message.
    """

    rule_type: ActionType
    condition_logic_type: LogicType
    conditions: List[TradeCondition]
    actions: list[str] = []

    def evaluate(
        self,
        snapshot: "MarketModel",
        date=date,
        trade: Optional["Trades"] = None,
        trade_schedule: Optional[TradeSchedule] = None,
    ):
        """Evaluates the rule based on the trade data."""
        result: bool = False
        match self.condition_logic_type:
            case LogicType.AND:
                result = all(
                    condition.evaluate(
                        data=snapshot,
                        date=date,
                        trade=trade,
                        trade_schedule=trade_schedule,
                    )
                    for condition in self.conditions
                )
            case LogicType.OR:
                result = any(
                    condition.evaluate(
                        data=snapshot,
                        date=date,
                        trade=trade,
                        trade_schedule=trade_schedule,
                    )
                    for condition in self.conditions
                )
            case LogicType.NOT:
                if len(self.conditions) != 1:
                    raise ValueError("NOT logic requires exactly one condition.")
                result = not self.conditions[0].evaluate(
                    data=snapshot, date=date, trade=trade, trade_schedule=trade_schedule
                )
            case LogicType.XOR:
                if len(self.conditions) != 2:
                    raise ValueError("XOR logic requires exactly two conditions.")
                result = bool(
                    self.conditions[0].evaluate(
                        data=snapshot,
                        date=date,
                        trade=trade,
                        trade_schedule=trade_schedule,
                    )
                ) ^ bool(
                    self.conditions[1].evaluate(
                        data=snapshot,
                        date=date,
                        trade=trade,
                        trade_schedule=trade_schedule,
                    )
                )
            case _:
                raise ValueError(
                    f"Invalid logic specified. Use {LogicType._value2member_map_}."
                )
        return result


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
