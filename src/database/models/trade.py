# src/database/models/trade.py - Trade model
from datetime import datetime
from typing import Dict, Optional

class Trade:
    def __init__(self, data: dict = None):
        data = data or {}
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.strategy = data.get('strategy')
        self.symbol = data.get('symbol')
        self.side = data.get('side')
        self.quantity = data.get('quantity', 0)
        self.entry_price = data.get('entry_price', 0)
        self.exit_price = data.get('exit_price')
        self.profit = data.get('profit')
        self.roi = data.get('roi')
        self.status = data.get('status', 'open')
        self.orders = data.get('orders', [])
        self.created_at = data.get('created_at', datetime.now())
        self.closed_at = data.get('closed_at')
        
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'strategy': self.strategy,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'profit': self.profit,
            'roi': self.roi,
            'status': self.status,
            'orders': self.orders,
            'created_at': self.created_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }