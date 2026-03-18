# src/core/strategies/base.py - Base strategy class
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseStrategy(ABC):
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.active_positions = {}
        
    @abstractmethod
    async def scan(self, market_data: Dict) -> List[Dict]:
        """Scan for opportunities"""
        pass
        
    @abstractmethod
    async def execute(self, opportunity: Dict) -> Dict:
        """Execute trade"""
        pass
        
    async def calculate_risk(self, opportunity: Dict) -> float:
        """Calculate risk score (0-1)"""
        return 0.3  # Default risk