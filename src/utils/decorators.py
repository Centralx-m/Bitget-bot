# src/utils/decorators.py - Utility decorators
import functools
import time
import logging
from typing import Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}. Retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

def rate_limit(calls: int = 10, period: int = 60):
    """Rate limiting decorator"""
    def decorator(func: Callable) -> Callable:
        last_reset = time.time()
        calls_made = 0
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            nonlocal last_reset, calls_made
            
            now = time.time()
            if now - last_reset > period:
                calls_made = 0
                last_reset = now
                
            if calls_made >= calls:
                wait_time = period - (now - last_reset)
                logger.warning(f"Rate limit reached for {func.__name__}. Waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                calls_made = 0
                last_reset = time.time()
                
            calls_made += 1
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_execution_time(func: Callable) -> Callable:
    """Log function execution time"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        logger.debug(f"{func.__name__} executed in {end - start:.3f}s")
        return result
    return wrapper