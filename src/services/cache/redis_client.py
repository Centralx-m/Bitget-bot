# src/services/cache/redis_client.py - Redis cache client
import redis.asyncio as redis
import json
import logging
from typing import Optional, Any
from utils.constants import Config

class RedisClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.connected = False
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = await redis.from_url(
                Config.REDIS_URL,
                decode_responses=True
            )
            await self.client.ping()
            self.connected = True
            self.logger.info("✅ Connected to Redis")
        except Exception as e:
            self.logger.error(f"❌ Redis connection failed: {e}")
            
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.connected:
                await self.connect()
                
            value = await self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            self.logger.error(f"Error getting {key}: {e}")
            return None
            
    async def set(self, key: str, value: Any, expire: int = 300):
        """Set value in cache"""
        try:
            if not self.connected:
                await self.connect()
                
            await self.client.setex(
                key,
                expire,
                json.dumps(value, default=str)
            )
        except Exception as e:
            self.logger.error(f"Error setting {key}: {e}")
            
    async def delete(self, key: str):
        """Delete from cache"""
        try:
            if not self.connected:
                await self.connect()
                
            await self.client.delete(key)
        except Exception as e:
            self.logger.error(f"Error deleting {key}: {e}")
            
    async def incr(self, key: str) -> int:
        """Increment counter"""
        try:
            if not self.connected:
                await self.connect()
                
            return await self.client.incr(key)
        except Exception as e:
            self.logger.error(f"Error incrementing {key}: {e}")
            return 0