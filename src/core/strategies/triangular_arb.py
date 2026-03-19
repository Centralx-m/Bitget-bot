# src/core/strategies/triangular_arb.py - Triangular arbitrage
from .base import BaseStrategy
import asyncio
import logging
from typing import Dict, List
from utils.math_utils import MathUtils

class TriangularArbitrage(BaseStrategy):
    def __init__(self, config: Dict):
        super().__init__("Triangular Arbitrage", config)
        self.MIN_PROFIT = 0.002  # 0.2%
        self.MAX_SLIPPAGE = 0.001  # 0.1%
        
    async def scan(self, market_data: Dict) -> List[Dict]:
        """Scan for triangular arbitrage opportunities"""
        opportunities = []
        
        # Define currency cycles
        cycles = [
            ['USDT', 'BTC', 'ETH', 'USDT'],
            ['USDT', 'ETH', 'BTC', 'USDT'],
            ['USDT', 'SOL', 'BTC', 'USDT'],
            ['USDT', 'BTC', 'SOL', 'USDT']
        ]
        
        for cycle in cycles:
            try:
                # Get prices for each pair
                prices = []
                for i in range(3):
                    pair = f"{cycle[i]}/{cycle[i+1]}"
                    if pair in market_data:
                        prices.append(market_data[pair]['last'])
                    else:
                        # Try reverse pair
                        reverse = f"{cycle[i+1]}/{cycle[i]}"
                        if reverse in market_data:
                            prices.append(1 / market_data[reverse]['last'])
                        else:
                            break
                            
                if len(prices) != 3:
                    continue
                    
                # Calculate arbitrage profit
                start_amount = 1000  # Base amount
                step1 = start_amount / prices[0]
                step2 = step1 * prices[1]
                step3 = step2 * prices[2]
                
                profit = step3 - start_amount
                roi = profit / start_amount
                
                # Check if profitable after fees
                net_roi = roi - (self.config.get('fees', 0.001) * 3) - self.MAX_SLIPPAGE
                
                if net_roi > self.MIN_PROFIT:
                    risk = await self.calculate_risk({
                        'cycle': cycle,
                        'prices': prices,
                        'roi': net_roi
                    })
                    
                    opportunities.append({
                        'strategy': self.name,
                        'cycle': ' → '.join(cycle),
                        'prices': prices,
                        'expected_roi': net_roi,
                        'expected_profit': net_roi * self.config.get('position_size', 100),
                        'risk': risk,
                        'confidence': min(net_roi * 100, 1.0),
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                self.logger.debug(f"Error scanning cycle {cycle}: {e}")
                continue
                
        return opportunities
        
    async def execute(self, opportunity: Dict) -> Dict:
        """Execute triangular arbitrage"""
        try:
            cycle = opportunity['cycle'].split(' → ')
            prices = opportunity['prices']
            
            # Execute three trades in sequence
            orders = []
            
            # Trade 1: USDT -> A
            pair1 = f"{cycle[1]}/{cycle[0]}"
            amount1 = self.config.get('position_size', 100) / prices[0]
            
            # In production, would execute actual orders
            orders.append({
                'pair': pair1,
                'side': 'buy',
                'amount': amount1,
                'price': prices[0]
            })
            
            await asyncio.sleep(0.5)  # Wait for order to fill
            
            # Trade 2: A -> B
            pair2 = f"{cycle[2]}/{cycle[1]}"
            amount2 = amount1 * prices[1]
            orders.append({
                'pair': pair2,
                'side': 'buy',
                'amount': amount2,
                'price': prices[1]
            })
            
            await asyncio.sleep(0.5)
            
            # Trade 3: B -> USDT
            pair3 = f"{cycle[0]}/{cycle[2]}"
            amount3 = amount2
            orders.append({
                'pair': pair3,
                'side': 'sell',
                'amount': amount3,
                'price': prices[2]
            })
            
            # Calculate actual profit
            final_amount = amount3 * prices[2]
            initial_amount = self.config.get('position_size', 100)
            profit = final_amount - initial_amount
            
            result = {
                'success': True,
                'strategy': self.name,
                'cycle': opportunity['cycle'],
                'orders': orders,
                'profit': profit,
                'roi': profit / initial_amount,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.update_metrics(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing triangular arbitrage: {e}")
            return {'success': False, 'error': str(e)}