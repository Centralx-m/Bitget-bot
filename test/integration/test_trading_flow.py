# tests/integration/test_trading_flow.py - Integration tests
import pytest
import asyncio
from src.core.engine.trading_engine import TradingEngine
from src.exchanges.bitget import BitgetClient
from src.services.firebase import FirebaseService

class TestTradingFlow:
    @pytest.mark.asyncio
    async def test_full_trading_cycle(self):
        """Test complete trading cycle"""
        # Initialize components
        engine = TradingEngine()
        await engine.initialize()
        
        # Run scan
        market_data = await engine._fetch_market_data()
        opportunities = await engine.strategy_manager.scan_all(market_data)
        
        assert isinstance(opportunities, list)
        
        # Score opportunities
        scored = await engine._score_opportunities(opportunities)
        assert len(scored) <= len(opportunities)
        
        await engine.shutdown()
        
    @pytest.mark.asyncio
    async def test_bitget_connection(self):
        """Test Bitget connection"""
        client = BitgetClient()
        connected = await client.connect()
        assert connected is True
        
        balance = await client.get_balance()
        assert isinstance(balance, dict)
        
    @pytest.mark.asyncio
    async def test_firebase_connection(self):
        """Test Firebase connection"""
        firebase = FirebaseService()
        firebase.initialize()
        
        # Test write
        trade_id = await firebase.save_trade({
            'test': True,
            'timestamp': 'test'
        })
        assert trade_id is not None