# src/services/trading/order_validator.py - Order validation
import logging
from typing import Dict, Optional
from utils.constants import Config

class OrderValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_order(self, order: Dict, portfolio: Dict) -> tuple[bool, Optional[str]]:
        """Validate order before execution"""
        
        # Check minimum order size
        if order.get('amount', 0) < Config.MIN_TRADE_SIZE:
            return False, f"Order amount too small: {order.get('amount', 0)} < {Config.MIN_TRADE_SIZE}"
            
        # Check maximum position size
        if order.get('amount', 0) > Config.MAX_POSITION_SIZE:
            return False, f"Order amount too large: {order.get('amount', 0)} > {Config.MAX_POSITION_SIZE}"
            
        # Check available capital
        required_capital = order.get('amount', 0) * order.get('price', 0)
        if required_capital > portfolio.get('available_capital', 0):
            return False, f"Insufficient capital: ${required_capital:.2f} needed, ${portfolio.get('available_capital', 0):.2f} available"
            
        # Check concurrent trades limit
        if portfolio.get('open_positions', 0) >= Config.MAX_CONCURRENT_TRADES:
            return False, f"Max concurrent trades reached: {portfolio.get('open_positions', 0)}"
            
        # Check daily loss limit
        if portfolio.get('daily_pnl', 0) <= -Config.MAX_DAILY_LOSS:
            return False, f"Daily loss limit reached: ${portfolio.get('daily_pnl', 0):.2f}"
            
        # Validate price reasonability
        if order.get('price', 0) <= 0:
            return False, "Invalid price"
            
        return True, None