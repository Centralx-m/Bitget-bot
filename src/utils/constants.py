# src/utils/constants.py - Configuration with your credentials
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bitget API - Your actual credentials
    BITGET_API_KEY = os.getenv('BITGET_API_KEY', 'bg_ffcbb26a743c6f3617a03e4edb87aa3f')
    BITGET_API_SECRET = os.getenv('BITGET_API_SECRET', 'e397e3420dbb6a1b48dfef734e6ef8d6aaf29ee44a044d51dd1742a8143c0693')
    BITGET_API_PASSPHRASE = os.getenv('BITGET_API_PASSPHRASE', '02703242')
    BITGET_API_BASE_URL = os.getenv('BITGET_API_BASE_URL', 'https://api.bitget.com')
    
    # Firebase - Your actual config
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'xtaagc')
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', 'AIzaSyCOcCDPqRSlAMJJBEeNchTA1qO9tl9Nldw')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', 'xtaagc.firebaseapp.com')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', 'xtaagc.firebasestorage.app')
    FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', '256073982437')
    FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', '1:256073982437:android:0c54368d54e260cba98f0c')
    
    # Server
    NODE_ENV = os.getenv('NODE_ENV', 'development')
    PORT = int(os.getenv('PORT', '8000'))
    API_VERSION = os.getenv('API_VERSION', 'v1')
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'xtaagc-super-secret-key-2024')
    JWT_EXPIRES_IN = os.getenv('JWT_EXPIRES_IN', '7d')
    
    # Trading
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '1000'))
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '100'))
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '50'))
    MAX_CONCURRENT_TRADES = int(os.getenv('MAX_CONCURRENT_TRADES', '5'))
    SCAN_INTERVAL_SECONDS = int(os.getenv('SCAN_INTERVAL_SECONDS', '60'))
    TARGET_DAILY_ROI = float(os.getenv('TARGET_DAILY_ROI', '1.0'))
    MAX_DRAWDOWN = float(os.getenv('MAX_DRAWDOWN', '15'))
    REINVEST_RATE = float(os.getenv('REINVEST_RATE', '80'))
    
    # Enabled Strategies
    ENABLED_STRATEGIES = os.getenv('ENABLED_STRATEGIES', 'triangular,funding,grid,liquidation,flash_loan,cross_exchange').split(',')
    
    # Version
    VERSION = '1.0.0'