# src/services/analytics/risk_metrics.py - Risk analysis
import numpy as np
from typing import List, Dict
from scipy import stats

class RiskMetrics:
    def __init__(self):
        self.risk_free_rate = 0.02
        
    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0
        return np.percentile(returns, (1 - confidence) * 100)
        
    def calculate_cvar(self, returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        if not returns:
            return 0
        var = self.calculate_var(returns, confidence)
        return np.mean([r for r in returns if r <= var])
        
    def calculate_beta(self, returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta (market correlation)"""
        if len(returns) < 2 or len(market_returns) < 2:
            return 1.0
        covariance = np.cov(returns, market_returns)[0][1]
        variance = np.var(market_returns)
        return covariance / variance if variance > 0 else 1.0
        
    def calculate_alpha(self, returns: List[float], market_returns: List[float]) -> float:
        """Calculate alpha (excess return)"""
        beta = self.calculate_beta(returns, market_returns)
        expected_return = self.risk_free_rate + beta * (np.mean(market_returns) - self.risk_free_rate)
        return np.mean(returns) - expected_return
        
    def calculate_treynor_ratio(self, returns: List[float], market_returns: List[float]) -> float:
        """Calculate Treynor ratio"""
        beta = self.calculate_beta(returns, market_returns)
        if beta == 0:
            return 0
        return (np.mean(returns) - self.risk_free_rate) / beta
        
    def calculate_calmar_ratio(self, returns: List[float], max_drawdown: float) -> float:
        """Calculate Calmar ratio"""
        if max_drawdown == 0:
            return 0
        return (np.mean(returns) * 252) / abs(max_drawdown)
        
    def calculate_omega_ratio(self, returns: List[float], threshold: float = 0) -> float:
        """Calculate Omega ratio"""
        if not returns:
            return 1.0
        gains = sum([r - threshold for r in returns if r > threshold])
        losses = abs(sum([r - threshold for r in returns if r < threshold]))
        return gains / losses if losses > 0 else float('inf')