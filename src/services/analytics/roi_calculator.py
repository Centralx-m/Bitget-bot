# src/services/analytics/roi_calculator.py - Advanced ROI calculations
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta

class ROICalculator:
    def __init__(self):
        self.metrics = {}
        
    def calculate_roi(self, initial: float, final: float) -> float:
        """Calculate simple ROI"""
        return ((final - initial) / initial) * 100 if initial > 0 else 0
        
    def calculate_cagr(self, initial: float, final: float, years: float) -> float:
        """Calculate Compound Annual Growth Rate"""
        return ((final / initial) ** (1 / years) - 1) * 100
        
    def calculate_sharpe(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate / 252
        if np.std(excess_returns) == 0:
            return 0
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
    def calculate_sortino(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (uses downside deviation)"""
        if not returns:
            return 0
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate / 252
        downside_returns = returns_array[returns_array < 0]
        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return 0
        return np.mean(excess_returns) / np.std(downside_returns) * np.sqrt(252)
        
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Dict:
        """Calculate maximum drawdown"""
        if not equity_curve:
            return {'max_drawdown': 0, 'duration': 0}
            
        peak = equity_curve[0]
        max_drawdown = 0
        drawdown_start = 0
        drawdown_end = 0
        current_drawdown_start = 0
        
        for i, value in enumerate(equity_curve):
            if value > peak:
                peak = value
                current_drawdown_start = i
            drawdown = (peak - value) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                drawdown_start = current_drawdown_start
                drawdown_end = i
                
        return {
            'max_drawdown': max_drawdown,
            'start_date': drawdown_start,
            'end_date': drawdown_end,
            'duration': drawdown_end - drawdown_start
        }
        
    def calculate_win_rate(self, trades: List[Dict]) -> float:
        """Calculate win rate percentage"""
        if not trades:
            return 0
        winning_trades = len([t for t in trades if t.get('profit', 0) > 0])
        return (winning_trades / len(trades)) * 100
        
    def calculate_profit_factor(self, trades: List[Dict]) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        gross_profit = sum([t.get('profit', 0) for t in trades if t.get('profit', 0) > 0])
        gross_loss = abs(sum([t.get('profit', 0) for t in trades if t.get('profit', 0) < 0]))
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
    def calculate_expectancy(self, trades: List[Dict]) -> float:
        """Calculate average expectancy per trade"""
        if not trades:
            return 0
        return sum([t.get('profit', 0) for t in trades]) / len(trades)