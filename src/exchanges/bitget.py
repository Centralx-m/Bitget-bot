# src/exchanges/bitget.py - Bitget exchange client
import ccxt
import logging
from typing import Dict, Any

class BitgetClient:
    def __init__(self, api_key: str, secret: str, password: str):
        self.exchange = ccxt.bitget({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'enableRateLimit': True
        })
        
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker"""
        ticker = self.exchange.fetch_ticker(symbol)
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'volume': ticker['baseVolume']
        }
        
    async def create_order(self, symbol: str, side: str, amount: float, price: float = None):
        """Create order"""
        return self.exchange.create_order(
            symbol, 'market' if not price else 'limit',
            side, amount, price
        )