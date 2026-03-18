# src/core/strategies/triangular_arb.py - Triangular arbitrage
from .base import BaseStrategy
import asyncio
import logging

class TriangularArbitrage(BaseStrategy):
    def __init__(self, config):
        super().__init__("Triangular Arbitrage", config)
        self.MIN_PROFIT = 0.002  # 0.2%
        
    async def scan(self, market_data):
        opportunities = []
        cycles = self.generate_cycles()
        
        for cycle in cycles:
            profit = await self.calculate_profit(cycle)
            if profit > self.MIN_PROFIT:
                opportunities.append({
                    'cycle': cycle,
                    'profit': profit,
                    'confidence': min(profit * 100, 1.0)
                })
        return opportunities
        
    def generate_cycles(self):
        return [
            ['USDT', 'BTC', 'ETH', 'USDT'],
            ['USDT', 'SOL', 'BGB', 'USDT']
        ]