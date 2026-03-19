# src/core/strategies/grid_trading.py - Grid trading strategy
from .base import BaseStrategy
import numpy as np
from typing import Dict, List
from datetime import datetime

class GridTrading(BaseStrategy):
    def __init__(self, config: Dict):
        super().__init__("Grid Trading", config)
        self.grid_levels = config.get('grid_levels', 10)
        self.grid_range = config.get('grid_range', 0.05)  # 5% range
        
    async def scan(self, market_data: Dict) -> List[Dict]:
        """Scan for grid trading opportunities"""
        opportunities = []
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        
        for pair in pairs:
            try:
                price = market_data.get(pair, {}).get('last', 0)
                if not price:
                    continue
                    
                # Calculate volatility
                ohlcv = market_data.get(f"{pair}_ohlcv", [])
                if len(ohlcv) > 20:
                    closes = [c['close'] for c in ohlcv[-20:]]
                    returns = np.diff(closes) / closes[:-1]
                    volatility = np.std(returns) * np.sqrt(24 * 365)
                    
                    if 0.2 < volatility < 1.0:  # 20-100% annual volatility
                        lower_price = price * (1 - self.grid_range)
                        upper_price = price * (1 + self.grid_range)
                        
                        opportunities.append({
                            'strategy': self.name,
                            'pair': pair,
                            'current_price': price,
                            'lower_price': lower_price,
                            'upper_price': upper_price,
                            'grid_levels': self.grid_levels,
                            'volatility': volatility,
                            'expected_roi': volatility * 0.3,  # Capture 30% of volatility
                            'risk': 0.3,
                            'confidence': min(volatility, 1.0),
                            'timestamp': datetime.now().isoformat()
                        })
                        
            except Exception as e:
                self.logger.debug(f"Error scanning {pair}: {e}")
                
        return opportunities
        
    async def execute(self, opportunity: Dict) -> Dict:
        """Execute grid trading setup"""
        try:
            pair = opportunity['pair']
            lower = opportunity['lower_price']
            upper = opportunity['upper_price']
            levels = opportunity['grid_levels']
            
            # Calculate grid prices
            step = (upper - lower) / levels
            grid_prices = [lower + i * step for i in range(levels + 1)]
            
            # Create grid orders
            orders = []
            position_size = self.config.get('position_size', 100) / levels
            
            for i, price in enumerate(grid_prices[:-1]):
                # Place buy order at each grid level
                orders.append({
                    'pair': pair,
                    'side': 'buy',
                    'type': 'limit',
                    'price': price,
                    'amount': position_size / price,
                    'grid_level': i
                })
                
                # Place sell order at next level
                orders.append({
                    'pair': pair,
                    'side': 'sell',
                    'type': 'limit',
                    'price': grid_prices[i + 1],
                    'amount': position_size / grid_prices[i + 1],
                    'grid_level': i
                })
                
            result = {
                'success': True,
                'strategy': self.name,
                'pair': pair,
                'grid_orders': orders,
                'grid_range': [lower, upper],
                'grid_levels': levels,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.update_metrics(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing grid trading: {e}")
            return {'success': False, 'error': str(e)}