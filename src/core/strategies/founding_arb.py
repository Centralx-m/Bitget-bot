# src/core/strategies/funding_arb.py - Funding rate arbitrage
from .base import BaseStrategy
import logging
from typing import Dict, List
from datetime import datetime, timedelta

class FundingArbitrage(BaseStrategy):
    def __init__(self, config: Dict):
        super().__init__("Funding Arbitrage", config)
        self.MIN_FUNDING_RATE = 0.0001  # 0.01%
        self.FUNDING_INTERVAL = 8  # hours
        
    async def scan(self, market_data: Dict) -> List[Dict]:
        """Scan for funding rate arbitrage opportunities"""
        opportunities = []
        
        # Pairs to scan
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        
        for pair in pairs:
            try:
                # Get funding rate from Bitget futures
                funding_rate = market_data.get(f"{pair}_funding", {}).get('rate', 0)
                
                if abs(funding_rate) < self.MIN_FUNDING_RATE:
                    continue
                    
                # Calculate annualized return
                annualized = abs(funding_rate) * (24 / self.FUNDING_INTERVAL) * 365
                
                # Get spot and futures prices
                spot_price = market_data.get(pair, {}).get('last', 0)
                futures_price = market_data.get(f"{pair}_perp", {}).get('last', spot_price)
                
                # Calculate basis
                basis = (futures_price - spot_price) / spot_price
                
                risk = await self.calculate_risk({
                    'funding_rate': funding_rate,
                    'basis': basis
                })
                
                opportunities.append({
                    'strategy': self.name,
                    'pair': pair,
                    'funding_rate': funding_rate,
                    'annualized_return': annualized,
                    'basis': basis,
                    'spot_price': spot_price,
                    'futures_price': futures_price,
                    'direction': 'long_spot_short_futures' if funding_rate > 0 else 'short_spot_long_futures',
                    'expected_roi': abs(funding_rate) * (24 / self.FUNDING_INTERVAL),
                    'risk': risk,
                    'confidence': min(abs(funding_rate) * 1000, 1.0),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.debug(f"Error scanning {pair}: {e}")
                
        return opportunities
        
    async def execute(self, opportunity: Dict) -> Dict:
        """Execute funding arbitrage"""
        try:
            pair = opportunity['pair']
            direction = opportunity['direction']
            size = self.config.get('position_size', 100)
            
            orders = []
            
            if direction == 'long_spot_short_futures':
                # Buy spot
                orders.append({
                    'pair': pair,
                    'side': 'buy',
                    'type': 'spot',
                    'amount': size / opportunity['spot_price']
                })
                
                # Sell futures
                orders.append({
                    'pair': f"{pair}_PERP",
                    'side': 'sell',
                    'type': 'futures',
                    'amount': size / opportunity['futures_price']
                })
            else:
                # Short spot (need margin)
                orders.append({
                    'pair': pair,
                    'side': 'sell',
                    'type': 'margin',
                    'amount': size / opportunity['spot_price']
                })
                
                # Buy futures
                orders.append({
                    'pair': f"{pair}_PERP",
                    'side': 'buy',
                    'type': 'futures',
                    'amount': size / opportunity['futures_price']
                })
                
            result = {
                'success': True,
                'strategy': self.name,
                'pair': pair,
                'direction': direction,
                'orders': orders,
                'funding_rate': opportunity['funding_rate'],
                'expected_daily_profit': size * abs(opportunity['funding_rate']) * (24 / self.FUNDING_INTERVAL),
                'timestamp': datetime.now().isoformat()
            }
            
            await self.update_metrics(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing funding arbitrage: {e}")
            return {'success': False, 'error': str(e)}