# src/services/trading/position_sizer.py - Position sizing algorithms
import math
from typing import Dict
import numpy as np

class PositionSizer:
    def __init__(self):
        self.methods = ['fixed', 'percent', 'kelly', 'risk_based']
        
    def calculate_position_size(self, method: str, capital: float, params: Dict) -> float:
        """Calculate position size based on method"""
        if method == 'fixed':
            return self._fixed_sizing(capital, params)
        elif method == 'percent':
            return self._percent_sizing(capital, params)
        elif method == 'kelly':
            return self._kelly_sizing(capital, params)
        elif method == 'risk_based':
            return self._risk_based_sizing(capital, params)
        else:
            return self._fixed_sizing(capital, params)
            
    def _fixed_sizing(self, capital: float, params: Dict) -> float:
        """Fixed position sizing"""
        return params.get('fixed_amount', 100)
        
    def _percent_sizing(self, capital: float, params: Dict) -> float:
        """Percentage of capital sizing"""
        percent = params.get('percent', 10)  # Default 10%
        return capital * (percent / 100)
        
    def _kelly_sizing(self, capital: float, params: Dict) -> float:
        """Kelly Criterion sizing"""
        win_rate = params.get('win_rate', 0.5)
        avg_win = params.get('avg_win', 0)
        avg_loss = params.get('avg_loss', 0)
        
        if avg_loss == 0:
            return capital * 0.02  # Default to 2%
            
        # Kelly formula: f* = (p * b - q) / b
        # where b = avg_win/avg_loss, p = win_rate, q = 1-p
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - p
        
        kelly_percent = (p * b - q) / b
        # Use half-kelly for safety
        safe_kelly = max(0, min(kelly_percent * 0.5, 0.25))
        
        return capital * safe_kelly
        
    def _risk_based_sizing(self, capital: float, params: Dict) -> float:
        """Risk-based position sizing"""
        risk_percent = params.get('risk_percent', 1)  # 1% risk per trade
        stop_loss = params.get('stop_loss_percent', 5)  # 5% stop loss
        
        risk_amount = capital * (risk_percent / 100)
        position_size = risk_amount / (stop_loss / 100)
        
        return position_size
        
    def calculate_lot_size(self, quantity: float, min_size: float, step: float) -> float:
        """Calculate lot size based on exchange requirements"""
        lots = math.floor(quantity / step)
        return max(lots * step, min_size)