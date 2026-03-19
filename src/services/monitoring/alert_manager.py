# src/services/monitoring/alert_manager.py - Alert management system
import asyncio
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from services.notification.telegram import TelegramNotifier
from services.notification.discord import DiscordNotifier
from services.notification.email import EmailNotifier

class AlertManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.telegram = TelegramNotifier()
        self.discord = DiscordNotifier()
        self.email = EmailNotifier()
        self.alert_history = []
        self.thresholds = {
            'daily_loss': -50,  # -$50 daily loss alert
            'drawdown': 15,      # 15% drawdown alert
            'profit_taking': 100, # $100 profit alert
            'connection_loss': 1  # Connection loss alert
        }
        
    async def check_alerts(self, metrics: Dict):
        """Check all alert conditions"""
        alerts = []
        
        # Check daily loss
        if metrics.get('daily_pnl', 0) < self.thresholds['daily_loss']:
            alerts.append({
                'type': 'daily_loss',
                'severity': 'high',
                'message': f"Daily loss limit reached: ${metrics['daily_pnl']:.2f}"
            })
            
        # Check drawdown
        if metrics.get('drawdown', 0) > self.thresholds['drawdown']:
            alerts.append({
                'type': 'drawdown',
                'severity': 'high',
                'message': f"Drawdown exceeded: {metrics['drawdown']:.1f}%"
            })
            
        # Check profit taking
        if metrics.get('daily_profit', 0) > self.thresholds['profit_taking']:
            alerts.append({
                'type': 'profit_taking',
                'severity': 'low',
                'message': f"Daily profit target reached: ${metrics['daily_profit']:.2f}"
            })
            
        # Send alerts
        for alert in alerts:
            await self.send_alert(alert)
            
    async def send_alert(self, alert: Dict):
        """Send alert through all channels"""
        self.alert_history.append({
            **alert,
            'timestamp': datetime.now().isoformat()
        })
        
        # Send based on severity
        if alert['severity'] == 'high':
            await self.telegram.send_alert(alert['message'])
            await self.discord.send_alert(alert['message'])
            await self.email.send_alert(alert['message'])
        elif alert['severity'] == 'medium':
            await self.telegram.send_message(alert['message'])
        else:
            # Log only
            self.logger.info(f"Alert: {alert['message']}")
            
    async def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """Get recent alert history"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            a for a in self.alert_history
            if datetime.fromisoformat(a['timestamp']) > cutoff
        ]