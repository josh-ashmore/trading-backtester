"""Enums for rules."""

from enum import Enum


class LogicType(str, Enum):
    """Logic Type Enum."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    XOR = "XOR"


class ValueConditionType(str, Enum):
    """Value Condition Type Enum."""

    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUAL_TO = "equal_to"
    NOT_EQUAL_TO = "not_equal_to"
    GREATER_THAN_EQUAL_TO = "greater_than_or_equal_to"
    LESS_THAN_EQUAL_TO = "less_than_or_equal_to"
    IN_RANGE = "in_range"
    NOT_IN_RANGE = "not_in_range"


class ActionType(str, Enum):
    """Action Type Enum."""

    OPEN = "open"
    CLOSE = "close"
    STOPLOSS = "stoploss"
    TAKE_PROFIT = "takeprofit"
