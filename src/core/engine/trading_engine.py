# src/core/engine/trading_engine.py - Main trading engine
import asyncio
import logging
from typing import Dict, List
from exchanges.factory import ExchangeFactory
from strategies.base import BaseStrategy
from core.engine.risk_manager import RiskManager

class TradingEngine:
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.risk_manager = RiskManager()
        self.exchanges = ExchangeFactory()
        
    async def initialize(self):
        await self.exchanges.initialize_all()
        await self.load_strategies()
        logging.info("✅ Trading engine initialized")
        
    async def run(self):
        while True:
            try:
                opportunities = await self.scan_opportunities()
                if opportunities:
                    await self.execute_best(opportunities[:5])
                await asyncio.sleep(Config.SCAN_INTERVAL)
            except Exception as e:
                logging.error(f"Engine error: {e}")