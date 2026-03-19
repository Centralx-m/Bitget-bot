# src/workers/execution_worker.py - Background trade executor
import asyncio
import logging
from core.engine.trading_engine import TradingEngine

class ExecutionWorker:
    def __init__(self, engine: TradingEngine):
        self.engine = engine
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
    async def start(self):
        """Start the worker"""
        self.is_running = True
        self.logger.info("Execution worker started")
        
        while self.is_running:
            try:
                # Get pending opportunities
                opportunities = await self.engine.cache.get('latest_opportunities') or []
                
                # Execute top opportunities
                if opportunities:
                    scored = await self.engine._score_opportunities(opportunities)
                    await self.engine._execute_opportunities(scored[:3])
                    
                await asyncio.sleep(10)  # Execute every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in execution worker: {e}")
                await asyncio.sleep(30)
                
    async def stop(self):
        """Stop the worker"""
        self.is_running = False
        self.logger.info("Execution worker stopped")