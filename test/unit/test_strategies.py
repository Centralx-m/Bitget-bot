# tests/unit/test_strategies.py - Unit tests for strategies
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.core.strategies.triangular_arb import TriangularArbitrage
from src.core.strategies.funding_arb import FundingArbitrage
from src.core.strategies.grid_trading import GridTrading

class TestStrategies:
    @pytest.mark.asyncio
    async def test_triangular_arb_scan(self):
        """Test triangular arbitrage scanning"""
        config = {'position_size': 100, 'fees': 0.001}
        strategy = TriangularArbitrage(config)
        
        market_data = {
            'BTC/USDT': {'last': 50000},
            'ETH/BTC': {'last': 0.05},
            'ETH/USDT': {'last': 2500}
        }
        
        opportunities = await strategy.scan(market_data)
        assert isinstance(opportunities, list)
        
    @pytest.mark.asyncio
    async def test_funding_arb_scan(self):
        """Test funding arbitrage scanning"""
        config = {'position_size': 100}
        strategy = FundingArbitrage(config)
        
        market_data = {
            'BTC/USDT': {'last': 50000},
            'BTC/USDT_funding': {'rate': 0.0001}
        }
        
        opportunities = await strategy.scan(market_data)
        assert isinstance(opportunities, list)
        
    @pytest.mark.asyncio
    async def test_grid_trading_scan(self):
        """Test grid trading scanning"""
        config = {'position_size': 100, 'grid_levels': 10}
        strategy = GridTrading(config)
        
        market_data = {
            'BTC/USDT': {'last': 50000},
            'BTC/USDT_ohlcv': [{'close': 50000} for _ in range(30)]
        }
        
        opportunities = await strategy.scan(market_data)
        assert isinstance(opportunities, list)