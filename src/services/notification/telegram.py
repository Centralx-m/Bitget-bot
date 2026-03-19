# src/services/notification/telegram.py - Telegram bot
import logging
from typing import Dict
import aiohttp
from utils.constants import Config

class TelegramNotifier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    async def send_message(self, text: str):
        """Send message to Telegram"""
        try:
            if not self.bot_token or not self.chat_id:
                return
                
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/sendMessage"
                data = {
                    'chat_id': self.chat_id,
                    'text': text,
                    'parse_mode': 'HTML'
                }
                async with session.post(url, json=data) as response:
                    if response.status != 200:
                        self.logger.error(f"Telegram send failed: {await response.text()}")
                        
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
            
    async def send_trade_notification(self, trade: Dict):
        """Send trade notification"""
        emoji = "✅" if trade.get('profit', 0) > 0 else "🔴"
        profit = trade.get('profit', 0)
        
        message = f"""
{emoji} <b>Trade Executed</b>
Strategy: {trade.get('strategy', 'Unknown')}
Profit: ${profit:.2f}
ROI: {trade.get('roi', 0)*100:.2f}%
Time: {trade.get('timestamp', '')}
        """
        
        await self.send_message(message)
        
    async def send_alert(self, message: str):
        """Send alert"""
        await self.send_message(f"⚠️ <b>Alert</b>\n{message}")