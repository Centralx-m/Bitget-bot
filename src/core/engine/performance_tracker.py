# src/core/engine/performance_tracker.py - ROI tracking
import logging
from typing import Dict, List
from datetime import datetime, timedelta
import numpy as np
from services.firebase import FirebaseService
from services.cache.redis_client import RedisClient

class PerformanceTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.firebase = FirebaseService()
        self.cache = RedisClient()
        self.metrics = {
            'daily_roi': [],
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'total_loss': 0,
            'average_roi': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'best_trade': 0,
            'worst_trade': 0
        }
        
    async def start(self):
        """Start performance tracking"""
        await self.load_metrics()
        self.logger.info("✅ Performance tracker started")
        
    async def stop(self):
        """Stop performance tracking"""
        await self.save_metrics()
        self.logger.info("Performance tracker stopped")
        
    async def record_trade(self, trade: Dict):
        """Record trade performance"""
        try:
            self.metrics['total_trades'] += 1
            
            profit = trade.get('profit', 0)
            roi = trade.get('roi', 0)
            
            if profit > 0:
                self.metrics['winning_trades'] += 1
                self.metrics['total_profit'] += profit
                if profit > self.metrics['best_trade']:
                    self.metrics['best_trade'] = profit
            else:
                self.metrics['losing_trades'] += 1
                self.metrics['total_loss'] += abs(profit)
                if abs(profit) > self.metrics['worst_trade']:
                    self.metrics['worst_trade'] = abs(profit)
                    
            # Update daily ROI
            self.metrics['daily_roi'].append({
                'timestamp': datetime.now().isoformat(),
                'roi': roi,
                'profit': profit
            })
            
            # Keep only last 30 days
            cutoff = datetime.now() - timedelta(days=30)
            self.metrics['daily_roi'] = [
                d for d in self.metrics['daily_roi']
                if datetime.fromisoformat(d['timestamp']) > cutoff
            ]
            
            await self.calculate_metrics()
            await self.save_metrics()
            await self.firebase.update_portfolio('system', self.metrics)
            
        except Exception as e:
            self.logger.error(f"Error recording trade: {e}")
            
    async def record_cycle(self, cycle_time: float, opportunities: int):
        """Record scan cycle performance"""
        try:
            # Store in Redis for real-time monitoring
            await self.cache.set('last_cycle', {
                'time': cycle_time,
                'opportunities': opportunities,
                'timestamp': datetime.now().isoformat()
            }, 60)
        except Exception as e:
            self.logger.error(f"Error recording cycle: {e}")
            
    async def calculate_metrics(self):
        """Calculate performance metrics"""
        try:
            total_trades = self.metrics['total_trades']
            if total_trades > 0:
                # Win rate
                self.metrics['win_rate'] = (self.metrics['winning_trades'] / total_trades) * 100
                
                # Average ROI
                rois = [d['roi'] for d in self.metrics['daily_roi']]
                if rois:
                    self.metrics['average_roi'] = np.mean(rois) * 100
                    
                    # Sharpe ratio (assuming risk-free rate of 2%)
                    risk_free_rate = 0.02 / 365  # Daily risk-free rate
                    excess_returns = [r - risk_free_rate for r in rois]
                    if np.std(excess_returns) > 0:
                        self.metrics['sharpe_ratio'] = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(365)
                        
                # Profit factor
                if self.metrics['total_loss'] > 0:
                    self.metrics['profit_factor'] = self.metrics['total_profit'] / self.metrics['total_loss']
                    
                # Max drawdown
                cumulative = np.cumsum([d['profit'] for d in self.metrics['daily_roi']])
                running_max = np.maximum.accumulate(cumulative)
                drawdown = (cumulative - running_max) / running_max * 100
                self.metrics['max_drawdown'] = abs(min(drawdown)) if len(drawdown) > 0 else 0
                
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            
    async def get_roi_report(self) -> Dict:
        """Get ROI report"""
        return {
            'total_trades': self.metrics['total_trades'],
            'win_rate': f"{self.metrics.get('win_rate', 0):.2f}%",
            'total_profit': f"${self.metrics['total_profit']:.2f}",
            'average_roi': f"{self.metrics.get('average_roi', 0):.2f}%",
            'sharpe_ratio': f"{self.metrics.get('sharpe_ratio', 0):.2f}",
            'profit_factor': f"{self.metrics.get('profit_factor', 0):.2f}",
            'max_drawdown': f"{self.metrics.get('max_drawdown', 0):.2f}%",
            'best_trade': f"${self.metrics['best_trade']:.2f}",
            'worst_trade': f"${self.metrics['worst_trade']:.2f}"
        }
        
    async def load_metrics(self):
        """Load metrics from cache"""
        try:
            cached = await self.cache.get('performance_metrics')
            if cached:
                self.metrics.update(cached)
        except Exception as e:
            self.logger.error(f"Error loading metrics: {e}")
            
    async def save_metrics(self):
        """Save metrics to cache"""
        try:
            await self.cache.set('performance_metrics', self.metrics, 3600)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")