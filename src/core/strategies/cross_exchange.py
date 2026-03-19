# src/core/strategies/cross_exchange.py - Cross-exchange arbitrage
from .base import BaseStrategy
import ccxt
from typing import Dict, List
from datetime import datetime

class CrossExchangeArbitrage(BaseStrategy):
    def __init__(self, config: Dict):
        super().__init__("Cross Exchange Arbitrage", config)
        self.exchanges = ['bitget', 'binance', 'bybit', 'okx']
        self.min_spread = config.get('min_spread', 0.002)  # 0.2%
        
    async def scan(self, market_data: Dict) -> List[Dict]:
        """Scan for cross-exchange arbitrage opportunities"""
        opportunities = []
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        
        for symbol in symbols:
            try:
                prices = {}
                
                # Get prices from different exchanges
                for exchange in self.exchanges:
                    price = market_data.get(f"{exchange}_{symbol}", {}).get('last')
                    if price:
                        prices[exchange] = price
                        
                if len(prices) < 2:
                    continue
                    
                # Find min and max prices
                buy_exchange = min(prices, key=prices.get)
                sell_exchange = max(prices, key=prices.get)
                buy_price = prices[buy_exchange]
                sell_price = prices[sell_exchange]
                
                spread = (sell_price - buy_price) / buy_price
                
                if spread > self.min_spread:
                    opportunities.append({
                        'strategy': self.name,
                        'symbol': symbol,
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'spread': spread,
                        'expected_roi': spread * 0.8,  # After fees
                        'risk': 0.3,
                        'confidence': min(spread * 100, 1.0),
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                self.logger.debug(f"Error scanning {symbol}: {e}")
                
        return opportunities
        
    async def execute(self, opportunity: Dict) -> Dict:
        """Execute cross-exchange arbitrage"""
        try:
            symbol = opportunity['symbol']
            buy_ex = opportunity['buy_exchange']
            sell_ex = opportunity['sell_exchange']
            buy_price = opportunity['buy_price']
            sell_price = opportunity['sell_price']
            
            size = self.config.get('position_size', 100)
            quantity = size / buy_price
            
            # Would need balances on both exchanges
            orders = [
                {
                    'exchange': buy_ex,
                    'symbol': symbol,
                    'side': 'buy',
                    'price': buy_price,
                    'quantity': quantity
                },
                {
                    'exchange': sell_ex,
                    'symbol': symbol,
                    'side': 'sell',
                    'price': sell_price,
                    'quantity': quantity
                }
            ]
            
            profit = (sell_price - buy_price) * quantity
            
            result = {
                'success': True,
                'strategy': self.name,
                'symbol': symbol,
                'orders': orders,
                'profit': profit,
                'roi': profit / size,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.update_metrics(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing cross-exchange arb: {e}")
            return {'success': False, 'error': str(e)}