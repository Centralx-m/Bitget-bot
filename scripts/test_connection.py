#!/usr/bin/env python3
# scripts/test_connection.py - Test Bitget connection with your credentials

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.exchanges.bitget import BitgetClient
from src.utils.constants import Config

async def test_connection():
    """Test Bitget connection"""
    print("🔧 Testing Bitget connection...")
    print(f"API Key: {Config.BITGET_API_KEY[:10]}...")
    
    client = BitgetClient()
    
    # Test connection
    connected = await client.connect()
    if connected:
        print("✅ Successfully connected to Bitget!")
        
        # Get balance
        balance = await client.get_balance()
        print(f"💰 Balance: {balance}")
        
        # Get BTC price
        ticker = await client.get_ticker('BTC/USDT')
        print(f"📈 BTC/USDT: ${ticker['last']}")
        
        # Test funding rate
        funding = await client.get_funding_rate('BTC/USDT')
        print(f"💸 Funding Rate: {funding}")
        
    else:
        print("❌ Failed to connect to Bitget")
        print("Please check your API credentials")

if __name__ == "__main__":
    asyncio.run(test_connection())