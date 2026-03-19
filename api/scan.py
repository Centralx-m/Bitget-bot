# api/scan.py - Vercel serverless function for scanning
from http.server import BaseHTTPRequestHandler
import json
import asyncio
import logging
from src.core.engine.trading_engine import TradingEngine
from src.utils.constants import Config

# Global engine instance (reused across invocations)
engine = TradingEngine()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request - scan for opportunities"""
        try:
            # Run scan cycle
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize if needed
            if not hasattr(engine, 'initialized'):
                loop.run_until_complete(engine.initialize())
                engine.initialized = True
            
            # Run scan
            market_data = loop.run_until_complete(engine._fetch_market_data())
            opportunities = loop.run_until_complete(
                engine.strategy_manager.scan_all(market_data)
            )
            
            # Return results
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'opportunities_found': len(opportunities),
                'timestamp': str(datetime.now()),
                'data': opportunities[:10]  # Return top 10
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())