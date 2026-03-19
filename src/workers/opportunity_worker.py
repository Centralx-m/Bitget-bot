# src/workers/opportunity_worker.py - Background opportunity scanner
import asyncio
import logging
from datetime import datetime
from core.engine.trading_engine import TradingEngine

class OpportunityWorker:
    def __init__(self, engine: TradingEngine):
        self.engine = engine
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
    async def start(self):
        """Start the worker"""
        self.is_running = True
        self.logger.info("Opportunity worker started")
        
        while self.is_running:
            try:
                # Fetch market data
                market_data = await self.engine._fetch_market_data()
                
                # Scan for opportunities
                opportunities = await self.engine.strategy_manager.scan_all(market_data)
                
                # Store opportunities
                if opportunities:
                    await self.engine.cache.set('latest_opportunities', opportunities, 60)
                    
                await asyncio.sleep(5)  # Scan every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in opportunity worker: {e}")
                await asyncio.sleep(10)
                
    async def stop(self):
        """Stop the worker"""
        self.is_running = False
        self.logger.info("Opportunity worker stopped")