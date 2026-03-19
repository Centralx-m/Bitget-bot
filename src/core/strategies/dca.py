# src/core/strategies/dca.py - Dollar Cost Averaging strategy
from .base import BaseStrategy
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta

class DCAStrategy(BaseStrategy):
    def __init__(self, config: Dict):
        super().__init__("DCA Strategy", config)
        self.investment_frequency = config.get('frequency', 'daily')  # daily, weekly, monthly
        self.investment_amount = config.get('amount', 10)  # $10 per cycle
        
    async def scan(self, market_data: Dict) -> List[Dict]:
        """Check if it's time to DCA"""
        opportunities = []
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BGB/USDT']
        
        try:
            # Check last investment time
            last_investment = await self.get_last_investment()
            should_invest = False
            
            if self.investment_frequency == 'daily':
                should_invest = datetime.now() - last_investment > timedelta(days=1)
            elif self.investment_frequency == 'weekly':
                should_invest = datetime.now() - last_investment > timedelta(days=7)
            elif self.investment_frequency == 'monthly':
                should_invest = datetime.now() - last_investment > timedelta(days=30)
                
            if should_invest:
                for pair in pairs:
                    price = market_data.get(pair, {}).get('last', 0)
                    if price:
                        # Check if price is at a discount
                        avg_price = await self.get_average_price(pair)
                        discount = (avg_price - price) / avg_price if avg_price > 0 else 0
                        
                        opportunities.append({
                            'strategy': self.name,
                            'pair': pair,
                            'current_price': price,
                            'average_price': avg_price,
                            'discount': discount,
                            'amount': self.investment_amount,
                            'expected_roi': discount * 4,  # Annualized estimate
                            'risk': 0.1,  # Low risk
                            'confidence': 0.8,
                            'timestamp': datetime.now().isoformat()
                        })
                        
        except Exception as e:
            self.logger.error(f"Error in DCA scan: {e}")
            
        return opportunities
        
    async def execute(self, opportunity: Dict) -> Dict:
        """Execute DCA buy"""
        try:
            pair = opportunity['pair']
            price = opportunity['current_price']
            amount = opportunity['amount']
            
            quantity = amount / price
            
            order = {
                'pair': pair,
                'side': 'buy',
                'type': 'market',
                'amount': quantity,
                'price': price,
                'total': amount
            }
            
            # Update last investment time
            await self.set_last_investment()
            
            result = {
                'success': True,
                'strategy': self.name,
                'pair': pair,
                'order': order,
                'amount_invested': amount,
                'quantity': quantity,
                'price': price,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.update_metrics(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing DCA: {e}")
            return {'success': False, 'error': str(e)}
            
    async def get_last_investment(self) -> datetime:
        """Get last investment time"""
        # In production, would get from database
        return datetime.now() - timedelta(days=2)
        
    async def set_last_investment(self):
        """Set last investment time"""
        # In production, would save to database
        pass
        
    async def get_average_price(self, pair: str) -> float:
        """Get average price for pair"""
        # In production, would calculate from historical data
        return 50000 if pair == 'BTC/USDT' else 3000