# src/utils/math_utils.py - Math utilities
import numpy as np
from typing import List

class MathUtils:
    @staticmethod
    def calculate_roi(initial: float, final: float) -> float:
        """Calculate ROI"""
        return (final - initial) / initial if initial > 0 else 0
        
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0
            
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
            
        return (avg_return - risk_free_rate/252) / std_return * np.sqrt(252)
        
    @staticmethod
    def calculate_position_size(capital: float, risk_percent: float, stop_loss_percent: float) -> float:
        """Calculate position size based on risk"""
        risk_amount = capital * (risk_percent / 100)
        return risk_amount / (stop_loss_percent / 100)
        
    @staticmethod
    def calculate_slippage(price: float, slippage_percent: float, is_buy: bool) -> float:
        """Calculate price with slippage"""
        if is_buy:
            return price * (1 + slippage_percent / 100)
        else:
            return price * (1 - slippage_percent / 100)
            
    @staticmethod
    def calculate_moving_average(prices: List[float], period: int) -> List[float]:
        """Calculate moving average"""
        if len(prices) < period:
            return []
            
        result = []
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i-period+1:i+1]) / period
            result.append(avg)
        return result
        
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return []
            
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return [100]
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return [rsi]