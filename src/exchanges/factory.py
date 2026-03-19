# src/exchanges/factory.py - Exchange factory with Bitget
from typing import Dict, Optional
import logging
from .bitget import BitgetClient
from utils.constants import Config

class ExchangeFactory:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchanges = {}
        self.bitget = None
        
    async def initialize_all(self):
        """Initialize all exchanges"""
        # Initialize Bitget with your credentials
        self.bitget = BitgetClient()
        if await self.bitget.connect():
            self.exchanges['bitget'] = self.bitget
            self.logger.info("✅ Bitget initialized")
            
        # Add more exchanges as needed
        # self.binance = BinanceClient()
        # self.bybit = BybitClient()
        
    async def get_exchange(self, name: str = 'bitget'):
        """Get exchange instance"""
        return self.exchanges.get(name)
        
    async def shutdown_all(self):
        """Shutdown all exchanges"""
        self.exchanges.clear()
        self.logger.info("All exchanges shutdown")