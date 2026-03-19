# src/core/engine/portfolio_manager.py - Portfolio management
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from utils.constants import Config
from services.cache.redis_client import RedisClient
from services.firebase import FirebaseService

class PortfolioManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = RedisClient()
        self.firebase = FirebaseService()
        self.portfolio = {
            'total_capital': Config.INITIAL_CAPITAL,
            'available_capital': Config.INITIAL_CAPITAL,
            'allocated_capital': 0,
            'positions': [],
            'daily_pnl': 0,
            'total_pnl': 0,
            'win_rate': 0,
            'trades_today': 0
        }
        
    async def load_state(self):
        """Load portfolio state from cache"""
        try:
            cached = await self.cache.get('portfolio_state')
            if cached:
                self.portfolio.update(cached)
                self.logger.info("✅ Portfolio state loaded")
        except Exception as e:
            self.logger.error(f"Error loading portfolio state: {e}")
            
    async def save_state(self):
        """Save portfolio state to cache"""
        try:
            await self.cache.set('portfolio_state', self.portfolio, 3600)  # 1 hour
        except Exception as e:
            self.logger.error(f"Error saving portfolio state: {e}")
            
    async def add_trade(self, trade: Dict):
        """Add trade to portfolio"""
        try:
            # Update portfolio
            self.portfolio['allocated_capital'] += trade.get('capital', 0)
            self.portfolio['available_capital'] -= trade.get('capital', 0)
            self.portfolio['positions'].append(trade)
            
            # Update PnL if trade is closed
            if trade.get('profit'):
                self.portfolio['total_pnl'] += trade['profit']
                self.portfolio['daily_pnl'] += trade['profit']
                self.portfolio['trades_today'] += 1
                
                # Update win rate
                wins = len([t for t in self.portfolio['positions'] if t.get('profit', 0) > 0])
                total = len(self.portfolio['positions'])
                self.portfolio['win_rate'] = (wins / total * 100) if total > 0 else 0
                
            # Save to Firebase
            await self.firebase.save_trade(trade)
            await self.save_state()
            
        except Exception as e:
            self.logger.error(f"Error adding trade: {e}")
            
    async def update_positions(self, current_prices: Dict):
        """Update position values with current prices"""
        try:
            for position in self.portfolio['positions']:
                if position.get('status') == 'open':
                    symbol = position['symbol']
                    if symbol in current_prices:
                        current_price = current_prices[symbol]['last']
                        entry_price = position['entry_price']
                        quantity = position['quantity']
                        
                        # Calculate unrealized PnL
                        if position['side'] == 'buy':
                            unrealized_pnl = (current_price - entry_price) * quantity
                        else:
                            unrealized_pnl = (entry_price - current_price) * quantity
                            
                        position['unrealized_pnl'] = unrealized_pnl
                        
            await self.save_state()
            
        except Exception as e:
            self.logger.error(f"Error updating positions: {e}")
            
    async def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        return {
            'total_capital': self.portfolio['total_capital'],
            'available_capital': self.portfolio['available_capital'],
            'allocated_capital': self.portfolio['allocated_capital'],
            'daily_pnl': self.portfolio['daily_pnl'],
            'total_pnl': self.portfolio['total_pnl'],
            'win_rate': self.portfolio['win_rate'],
            'open_positions': len([p for p in self.portfolio['positions'] if p.get('status') == 'open']),
            'trades_today': self.portfolio['trades_today']
        }
        
    async def close_all_positions(self):
        """Close all open positions"""
        self.logger.info("Closing all positions...")
        self.portfolio['positions'] = []
        self.portfolio['allocated_capital'] = 0
        self.portfolio['available_capital'] = self.portfolio['total_capital']
        await self.save_state()