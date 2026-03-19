# src/core/strategies/base.py - Base strategy class
from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Optional
from datetime import datetime

class BaseStrategy(ABC):
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"strategy.{name}")
        self.active_positions = {}
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit': 0,
            'total_loss': 0
        }
        
    @abstractmethod
    async def scan(self, market_data: Dict) -> List[Dict]:
        """Scan for opportunities"""
        pass
        
    @abstractmethod
    async def execute(self, opportunity: Dict) -> Dict:
        """Execute trade"""
        pass
        
    async def validate(self, opportunity: Dict) -> bool:
        """Validate opportunity"""
        return True
        
    async def calculate_risk(self, opportunity: Dict) -> float:
        """Calculate risk score (0-1)"""
        # Base risk calculation
        risk = 0.3
        
        # Adjust based on volatility if available
        if 'volatility' in opportunity:
            risk += opportunity['volatility'] * 0.5
            
        return min(risk, 1.0)
        
    async def calculate_position_size(self, capital: float, risk: float) -> float:
        """Calculate position size based on risk"""
        return capital * (1 - risk) * 0.1  # Use 10% of available capital
        
    async def update_metrics(self, trade_result: Dict):
        """Update strategy metrics"""
        self.metrics['total_trades'] += 1
        
        profit = trade_result.get('profit', 0)
        if profit > 0:
            self.metrics['winning_trades'] += 1
            self.metrics['total_profit'] += profit
        else:
            self.metrics['total_loss'] += abs(profit)
            
    def get_status(self) -> Dict:
        """Get strategy status"""
        return {
            'name': self.name,
            'active_positions': len(self.active_positions),
            'metrics': self.metrics,
            'config': self.config
        }