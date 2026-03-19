# src/services/firebase.py - Firebase service with your credentials
import firebase_admin
from firebase_admin import credentials, firestore, auth
import json
import logging
from typing import Dict, List, Optional
from utils.constants import Config

class FirebaseService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        self.db = None
        self.auth = None
        
    def initialize(self):
        """Initialize Firebase with your credentials"""
        try:
            # Your Firebase config
            firebase_config = {
                "apiKey": Config.FIREBASE_API_KEY,
                "authDomain": Config.FIREBASE_AUTH_DOMAIN,
                "projectId": Config.FIREBASE_PROJECT_ID,
                "storageBucket": Config.FIREBASE_STORAGE_BUCKET,
                "messagingSenderId": Config.FIREBASE_MESSAGING_SENDER_ID,
                "appId": Config.FIREBASE_APP_ID
            }
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": Config.FIREBASE_PROJECT_ID,
                "private_key_id": "your-private-key-id",  # Add from your google-services.json
                "private_key": "your-private-key",  # Add from your google-services.json
                "client_email": "firebase-adminsdk@xtaagc.iam.gserviceaccount.com",
                "client_id": "your-client-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            })
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': f'https://{Config.FIREBASE_PROJECT_ID}.firebaseio.com',
                'storageBucket': Config.FIREBASE_STORAGE_BUCKET
            })
            
            self.db = firestore.client()
            self.auth = auth
            self.initialized = True
            self.logger.info("✅ Firebase initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Firebase initialization failed: {e}")
            
    async def save_trade(self, trade_data: Dict) -> str:
        """Save trade to Firestore"""
        try:
            if not self.initialized:
                self.initialize()
                
            doc_ref = self.db.collection('trades').document()
            trade_data['timestamp'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(trade_data)
            
            return doc_ref.id
        except Exception as e:
            self.logger.error(f"Error saving trade: {e}")
            return None
            
    async def get_trades(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user trades"""
        try:
            if not self.initialized:
                self.initialize()
                
            trades = self.db.collection('trades')\
                .where('user_id', '==', user_id)\
                .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
                
            return [{'id': t.id, **t.to_dict()} for t in trades]
        except Exception as e:
            self.logger.error(f"Error fetching trades: {e}")
            return []
            
    async def save_opportunity(self, opportunity: Dict) -> str:
        """Save detected opportunity"""
        try:
            if not self.initialized:
                self.initialize()
                
            doc_ref = self.db.collection('opportunities').document()
            opportunity['timestamp'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(opportunity)
            
            return doc_ref.id
        except Exception as e:
            self.logger.error(f"Error saving opportunity: {e}")
            return None
            
    async def update_portfolio(self, user_id: str, portfolio_data: Dict):
        """Update user portfolio"""
        try:
            if not self.initialized:
                self.initialize()
                
            self.db.collection('portfolios').document(user_id).set(
                portfolio_data, merge=True
            )
        except Exception as e:
            self.logger.error(f"Error updating portfolio: {e}")
            
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user data"""
        try:
            if not self.initialized:
                self.initialize()
                
            user = self.auth.get_user(user_id)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'created_at': user.user_metadata.creation_timestamp
            }
        except Exception as e:
            self.logger.error(f"Error getting user: {e}")
            return None
            
    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify Firebase token"""
        try:
            if not self.initialized:
                self.initialize()
                
            decoded_token = self.auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            self.logger.error(f"Error verifying token: {e}")
            return None