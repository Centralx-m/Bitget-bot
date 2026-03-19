# tests/unit/test_utils.py - Unit tests for utilities
import pytest
from src.utils.math_utils import MathUtils
from src.utils.validators import Validators

class TestMathUtils:
    def test_calculate_roi(self):
        roi = MathUtils.calculate_roi(1000, 1100)
        assert roi == 0.1
        
    def test_calculate_sharpe_ratio(self):
        returns = [0.01, 0.02, -0.01, 0.015, -0.005]
        sharpe = MathUtils.calculate_sharpe_ratio(returns)
        assert isinstance(sharpe, float)
        
    def test_calculate_position_size(self):
        size = MathUtils.calculate_position_size(10000, 2, 5)
        assert size == 4000
        
class TestValidators:
    def test_validate_email(self):
        assert Validators.validate_email("test@example.com") is True
        assert Validators.validate_email("invalid") is False
        
    def test_validate_password(self):
        valid, msg = Validators.validate_password("Test123!@#")
        assert valid is True
        
        valid, msg = Validators.validate_password("weak")
        assert valid is False
        
    def test_validate_symbol(self):
        assert Validators.validate_symbol("BTC/USDT") is True
        assert Validators.validate_symbol("BTCUSDT") is False