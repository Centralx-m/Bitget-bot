# src/core/strategies/liquidation.py - Liquidation sniping strategy
from .base import BaseStrategy
import numpy as np
from typing import Dict, List
from datetime import datetime

class LiquidationSniping(BaseStrategy):
    def __init__(self, config: Dict):
        super().__init__("Liquidation Sniping", config)
        self.min_liquidation_size = config.get('min_size', 10000)  # $10k min
        self.max_distance = config.get('max_distance', 0.02)  # 2% from liquidation
        
    async def scan(self, market_data: Dict) -> List[Dict]:
        """Scan for liquidation opportunities"""
        opportunities = []
        
        # Monitor positions near liquidation
        positions = market_data.get('positions', [])
        
        for pos in positions:
            try:
                liq_price = pos.get('liquidation_price')
                mark_price = pos.get('mark_price')
                size = pos.get('size', 0) * mark_price
                
                if not liq_price or not mark_price:
                    continue
                    
                distance = abs(mark_price - liq_price) / mark_price
                
                if distance < self.max_distance and size > self.min_liquidation_size:
                    side = 'buy' if pos.get('side') == 'long' else 'sell'
                    
                    opportunities.append({
                        'strategy': self.name,
                        'symbol': pos.get('symbol'),
                        'liquidation_price': liq_price,
                        'current_price': mark_price,
                        'distance': distance,
                        'position_size': size,
                        'side': side,
                        'expected_roi': distance * 5,  # Potential profit
                        'risk': 0.6,
                        'confidence': 1.0 - (distance / self.max_distance),
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                self.logger.debug(f"Error scanning liquidation: {e}")
                
        return opportunities
        
    async def execute(self, opportunity: Dict) -> Dict:
        """Execute liquidation snipe"""
        try:
            symbol = opportunity['symbol']
            liq_price = opportunity['liquidation_price']
            side = opportunity['side']
            size = self.config.get('position_size', 100)
            
            # Place order just above/below liquidation
            if side == 'buy':
                entry_price = liq_price * 1.001  # 0.1% above liquidation
            else:
                entry_price = liq_price * 0.999  # 0.1% below liquidation
                
            quantity = size / entry_price
            
            order = {
                'symbol': symbol,
                'side': side,
                'type': 'limit',
                'price': entry_price,
                'quantity': quantity,
                'stop_loss': entry_price * 0.98,  # 2% stop loss
                'take_profit': entry_price * 1.05  # 5% take profit
            }
            
            result = {
                'success': True,
                'strategy': self.name,
                'symbol': symbol,
                'order': order,
                'expected_profit': size * 0.03,  # 3% expected profit
                'timestamp': datetime.now().isoformat()
            }
            
            await self.update_metrics(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing liquidation snipe: {e}")
            return {'success': False, 'error': str(e)}