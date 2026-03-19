# src/utils/validators.py - Data validators
import re
from typing import Any, Dict, List, Optional

class Validators:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        return True, None
        
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate trading symbol format"""
        pattern = r'^[A-Z]{2,10}/[A-Z]{2,10}$'
        return bool(re.match(pattern, symbol))
        
    @staticmethod
    def validate_amount(amount: float, min_amount: float = 0) -> bool:
        """Validate trade amount"""
        return amount > min_amount
        
    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price"""
        return price > 0
        
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        return len(api_key) > 20 and not re.search(r'\s', api_key)
        
    @staticmethod
    def validate_config(config: Dict, required_fields: List[str]) -> tuple[bool, List[str]]:
        """Validate configuration has required fields"""
        missing = [field for field in required_fields if field not in config]
        return len(missing) == 0, missing