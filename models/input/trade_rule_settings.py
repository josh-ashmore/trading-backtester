"""Trade Rule Settings Model."""

from typing import TYPE_CHECKING, List
from pydantic import BaseModel, model_validator
from models.rules.enums import ActionType

if TYPE_CHECKING:
    from models.rules.rules import TradeRule
    from models.rules.execution import ExecutionRule


class TradeRuleSettings(BaseModel):
    """Trade Rule Settings.

    Need to define this better.
    """

    trade_rules: List["TradeRule"]
    execution_rules: List["ExecutionRule"]

    open_rules: list["TradeRule"] | None = None
    close_rules: list["TradeRule"] | None = None
    stoploss_rules: list["TradeRule"] | None = None
    takeprofit_rules: list["TradeRule"] | None = None

    @model_validator(mode="after")
    def post_validate_model(self):
        """Post validate model."""
        if self.open_rules is None:
            self.open_rules = [
                rule for rule in self.trade_rules if rule.rule_type == ActionType.OPEN
            ]
        if self.close_rules is None:
            self.close_rules = [
                rule for rule in self.trade_rules if rule.rule_type == ActionType.CLOSE
            ]
        if self.stoploss_rules is None:
            self.stoploss_rules = [
                rule
                for rule in self.trade_rules
                if rule.rule_type == ActionType.STOPLOSS
            ]
        if self.takeprofit_rules is None:
            self.takeprofit_rules = [
                rule
                for rule in self.trade_rules
                if rule.rule_type == ActionType.TAKE_PROFIT
            ]
        return self
