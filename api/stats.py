# api/stats.py - Get bot statistics
from http.server import BaseHTTPRequestHandler
import json
import asyncio
from src.core.engine.trading_engine import TradingEngine
from src.services.firebase import FirebaseService

engine = TradingEngine()
firebase = FirebaseService()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get bot statistics"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get portfolio summary
            portfolio = loop.run_until_complete(
                engine.portfolio_manager.get_portfolio_summary()
            )
            
            # Get performance metrics
            performance = loop.run_until_complete(
                engine.performance_tracker.get_roi_report()
            )
            
            response = {
                'success': True,
                'portfolio': portfolio,
                'performance': performance,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())