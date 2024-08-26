"""Risk Management Manager."""

from typing import List
from pydantic import BaseModel
from models.account.account import Account
from models.configs.risk_management_config import RiskManagementConfig
from models.trades.trades import Trades


class RiskManager(BaseModel):
    """Manager to handle different risk strategies."""

    management_config: RiskManagementConfig

    def apply_risk_management(self, account: Account, trades: List[Trades]):
        """Apply the risk strategies to the trades before execution."""
        if self.management_config.position_sizing:
            self.apply_position_sizing(
                account=account,
                trades=trades,
                max_position_size=self.management_config.position_sizing,
            )
        if self.management_config.stop_loss_pct:
            self.apply_stop_loss(
                account=account,
                trades=trades,
                stop_loss_pct=self.management_config.stop_loss_pct,
            )
        if self.management_config.portfolio_limit:
            self.apply_portfolio_limit(
                account=account,
                trades=trades,
                max_total_exposure=self.management_config.portfolio_limit,
            )
        if self.management_config.max_drawdown:
            self.apply_max_drawdown(
                account=account,
                trades=trades,
                max_drawdown=self.management_config.max_drawdown,
            )

    def apply_position_sizing(
        self, account: Account, trades: List[Trades], max_position_size: float
    ):
        """Adjust position sizes based on account size and max position size."""
        total_value = account.cash_balance + [trade.mtm() for trade in trades]
        for trade in trades:
            trade_size = trade.notional_amount
            if trade_size > total_value * max_position_size:
                trade.adjust_size(total_value * max_position_size)

    def apply_stop_loss(self, account: Account, trades: Trades, stop_loss_pct: float):
        """Implement stop-loss rules on trades."""
        for trade in trades:
            trade.set_stop_loss_level(trade.entry_price * (1 - stop_loss_pct))

    def apply_portfolio_limit(
        self, account: Account, trades: List[Trades], max_total_exposure: float
    ):
        """Ensure total portfolio exposure does not exceed a limit."""
        current_exposure = account.total_exposure()
        for trade in trades:
            if (
                current_exposure + trade.notional_amount
                > account.total_value() * max_total_exposure
            ):
                trade.adjust_size(
                    (account.total_value() * max_total_exposure) - current_exposure
                )

    def apply_max_drawdown(self, account: Account, trades: Trades, max_drawdown: float):
        """Manage trades to ensure portfolio drawdown doesn't exceed a max level."""
        # Implementation would require historical
        # performance tracking and applying drawdown limits
        pass
