# api/execute.py - Vercel serverless function for execution
from http.server import BaseHTTPRequestHandler
import json
import asyncio
from src.core.engine.trading_engine import TradingEngine
from src.services.firebase import FirebaseService

engine = TradingEngine()
firebase = FirebaseService()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Execute a trade"""
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # Execute trade
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if not hasattr(engine, 'initialized'):
                loop.run_until_complete(engine.initialize())
                engine.initialized = True
            
            # Execute opportunity
            result = loop.run_until_complete(
                engine.strategy_manager.execute_strategy(data)
            )
            
            # Save to Firebase
            if result and result.get('success'):
                loop.run_until_complete(
                    firebase.save_trade(result)
                )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'success': True,
                'result': result
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())