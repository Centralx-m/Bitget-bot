# src/main.py - Main application entry point
import asyncio
import logging
from core.engine.trading_engine import TradingEngine
from utils.constants import Config
from services.monitoring.logger import setup_logging

class XTAAGCBot:
    def __init__(self):
        self.engine = TradingEngine()
        self.running = False
        
    async def start(self):
        setup_logging()
        logging.info("🚀 Starting XTAAGC Bot...")
        await self.engine.initialize()
        self.running = True
        await self.engine.run()
        
    async def shutdown(self):
        logging.info("🛑 Shutting down...")
        await self.engine.shutdown()

if __name__ == "__main__":
    bot = XTAAGCBot()
    asyncio.run(bot.start())