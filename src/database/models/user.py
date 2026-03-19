# src/database/models/user.py - User model
from datetime import datetime
from typing import Optional

class User:
    def __init__(self, data: dict = None):
        data = data or {}
        self.id = data.get('id')
        self.email = data.get('email')
        self.username = data.get('username')
        self.password_hash = data.get('password_hash')
        self.api_keys = data.get('api_keys', {})
        self.role = data.get('role', 'user')
        self.created_at = data.get('created_at', datetime.now())
        self.updated_at = data.get('updated_at', datetime.now())
        
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }