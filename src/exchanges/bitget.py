# src/exchanges/bitget.py - Bitget exchange client with your credentials
import ccxt
import hmac
import hashlib
import time
import logging
from typing import Dict, List, Optional
from utils.constants import Config

class BitgetClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = Config.BITGET_API_KEY
        self.api_secret = Config.BITGET_API_SECRET
        self.api_passphrase = Config.BITGET_API_PASSPHRASE
        self.base_url = Config.BITGET_API_BASE_URL
        
        # Initialize CCXT exchange
        self.exchange = ccxt.bitget({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.api_passphrase,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
            }
        })
        
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Test connection to Bitget"""
        try:
            # Test API connection
            balance = await self.get_balance()
            self.is_connected = True
            self.logger.info("✅ Connected to Bitget successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Bitget: {e}")
            return False
            
    async def get_balance(self) -> Dict:
        """Get account balance"""
        try:
            balance = self.exchange.fetch_balance()
            result = {}
            
            for currency, data in balance['total'].items():
                if data > 0:
                    result[currency] = {
                        'free': balance['free'].get(currency, 0),
                        'used': balance['used'].get(currency, 0),
                        'total': data
                    }
            return result
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return {}
            
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': ticker['symbol'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'volume': ticker['baseVolume'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
            
    async def create_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """Create order on Bitget"""
        try:
            order_type = 'market' if price is None else 'limit'
            
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            
            self.logger.info(f"✅ Order created: {side} {amount} {symbol}")
            return order
        except Exception as e:
            self.logger.error(f"Error creating order: {e}")
            return None
            
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"✅ Order cancelled: {order_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False
            
    async def get_order_book(self, symbol: str, limit: int = 10) -> Dict:
        """Get order book"""
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return {
                'bids': orderbook['bids'][:limit],
                'asks': orderbook['asks'][:limit],
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error fetching orderbook: {e}")
            return None
            
    async def get_funding_rate(self, symbol: str) -> Dict:
        """Get funding rate for futures"""
        try:
            # For perpetual futures
            market_id = symbol.replace('/', '') + '_UMCBL'
            funding = self.exchange.fetch_funding_rate(market_id)
            return {
                'symbol': symbol,
                'funding_rate': funding['fundingRate'],
                'funding_time': funding['fundingTimestamp'],
                'next_funding_time': funding['nextFundingTimestamp']
            }
        except Exception as e:
            self.logger.error(f"Error fetching funding rate: {e}")
            return None
            
    async def get_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> List:
        """Get OHLCV data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            result = []
            for candle in ohlcv:
                result.append({
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            return result
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV: {e}")
            return []
            
    def generate_signature(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """Generate signature for authenticated requests"""
        message = timestamp + method + request_path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
        
    def get_headers(self, method: str, request_path: str, body: str = '') -> Dict:
        """Get authenticated headers"""
        timestamp = str(int(time.time()))
        signature = self.generate_signature(timestamp, method, request_path, body)
        
        return {
            'ACCESS-KEY': self.api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': self.api_passphrase,
            'Content-Type': 'application/json'
        }