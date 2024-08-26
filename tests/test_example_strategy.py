"""Test example strategy."""

from datetime import date
from models.account.account import Account
from models.input.input import (
    BaseStrategyInput,
    MarketDataSettings,
    TradeDataSettings,
    TradeRuleSettings,
)
from models.rules.comparison import DateField, PortfolioField, ValueField
from models.rules.rules import TradeRule, TradeCondition, ComparisonField
from models.rules.execution import (
    CallTrade,
    ExecutionRule,
    NotionalRule,
    PutTrade,
    TreasuryBillTrade,
)
from modules.orchestrator import BacktesterOrchestrator


def test_example_strategy(market_data):
    """Test example strategy."""
    market_data_settings = MarketDataSettings(
        spot_date=date(2024, 1, 1),
        underlying="GOLD",
        currency="USD",
        asset_class="CM",
        pricing_currencies_map={"USD": "USD OIS"},
    )
    trade_data_settings = TradeDataSettings()
    execution_rules = [
        ExecutionRule(
            rule_type="Spread",
            target_cost=0,
            trades=[
                PutTrade(
                    underlying="GOLD",
                    asset_class="CM",
                    direction="Buy",
                    strike=5,
                    strike_calculation="percent_otm",
                    notional_rule=NotionalRule(
                        rule_type="percentage_of_account", value=0.5
                    ),
                ),
                CallTrade(
                    underlying="GOLD",
                    asset_class="CM",
                    direction="Sell",
                    strike=None,
                    strike_calculation="abs",
                    notional_rule=NotionalRule(
                        rule_type="percentage_of_account", value=0.5
                    ),
                ),
            ],
        )
    ]
    put_call_trade_rules = TradeRuleSettings(
        trade_rules=[
            TradeRule(
                rule_type="open",
                conditions=[
                    TradeCondition(
                        comparison_one=ComparisonField(
                            field_settings=DateField(field="expiry")
                        ),
                        comparison_two=ComparisonField(
                            field_settings=DateField(field="current")
                        ),
                        type="equal_to",
                    ),
                ],
                condition_logic_type="AND",
            ),
            TradeRule(
                rule_type="close",
                conditions=[
                    TradeCondition(
                        comparison_one=ComparisonField(
                            field_settings=DateField(field="expiry")
                        ),
                        comparison_two=ComparisonField(
                            field_settings=DateField(field="current")
                        ),
                        type="equal_to",
                    ),
                ],
                condition_logic_type="AND",
            ),
        ],
        execution_rules=execution_rules,
    )
    treasury_trade_settings = TradeRuleSettings(
        trade_rules=[
            TradeRule(
                rule_type="open",
                conditions=[
                    TradeCondition(
                        comparison_one=ComparisonField(
                            field_settings=PortfolioField(field="no_open_trades")
                        ),
                        comparison_two=ComparisonField(
                            field_settings=ValueField(value=True)
                        ),
                        type="equal_to",
                    ),
                ],
                condition_logic_type="AND",
            ),
            TradeRule(
                rule_type="close",
                conditions=[
                    TradeCondition(
                        comparison_one=ComparisonField(
                            field_settings=PortfolioField(field="open_trades")
                        ),
                        comparison_two=ComparisonField(
                            field_settings=ValueField(value=True)
                        ),
                        type="equal_to",
                    ),
                ],
                condition_logic_type="AND",
            ),
        ],
        execution_rules=[
            ExecutionRule(
                rule_type="Buy",
                trades=[
                    TreasuryBillTrade(
                        underlying="US10Y",
                        direction="Buy",
                        notional_rule=NotionalRule(
                            rule_type="percentage_of_account", value=1
                        ),
                    )
                ],
            )
        ],
    )

    strategy_input = BaseStrategyInput(
        data=market_data,
        market_data_settings=market_data_settings,
        trade_data_settings=trade_data_settings,
        trade_rule_settings=[put_call_trade_rules, treasury_trade_settings],
        account=Account(currency="USD", initial_balance=5_000),
    )

    backtester = BacktesterOrchestrator(strategy_input=strategy_input)
    backtester.run()

    assert True
