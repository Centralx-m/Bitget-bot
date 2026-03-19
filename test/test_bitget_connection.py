# tests/test_bitget_connection.py - Test Bitget connection
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.exchanges.bitget import BitgetClient
from src.utils.constants import Config

async def test_bitget():
    """Test Bitget connection with your credentials"""
    print("="*50)
    print("🔧 TESTING BITGET CONNECTION")
    print("="*50)
    
    # Initialize client
    client = BitgetClient()
    
    # Test connection
    print("\n1️⃣ Testing connection...")
    connected = await client.connect()
    if connected:
        print("   ✅ Connected successfully")
    else:
        print("   ❌ Connection failed")
        return
        
    # Get balance
    print("\n2️⃣ Fetching balance...")
    balance = await client.get_balance()
    print(f"   Balance: {balance}")
    
    # Get BTC price
    print("\n3️⃣ Fetching BTC/USDT ticker...")
    ticker = await client.get_ticker('BTC/USDT')
    if ticker:
        print(f"   BTC/USDT: ${ticker['last']:.2f}")
        print(f"   Bid: ${ticker['bid']:.2f}")
        print(f"   Ask: ${ticker['ask']:.2f}")
        print(f"   Volume: {ticker['volume']:.2f}")
        
    # Get order book
    print("\n4️⃣ Fetching order book...")
    orderbook = await client.get_order_book('BTC/USDT', 5)
    if orderbook:
        print("   Top 5 Bids:")
        for bid in orderbook['bids'][:3]:
            print(f"     ${bid[0]:.2f} - {bid[1]:.4f}")
        print("   Top 5 Asks:")
        for ask in orderbook['asks'][:3]:
            print(f"     ${ask[0]:.2f} - {ask[1]:.4f}")
            
    # Get funding rate
    print("\n5️⃣ Fetching funding rate...")
    funding = await client.get_funding_rate('BTC/USDT')
    if funding:
        print(f"   Funding Rate: {funding['funding_rate']*100:.4f}%")
        
    print("\n" + "="*50)
    print("✅ All tests completed!")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(test_bitget())