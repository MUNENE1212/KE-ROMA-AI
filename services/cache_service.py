#!/usr/bin/env python3
"""
Caching service for KE-ROUMA app performance optimization
"""
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import hashlib

class CacheService:
    """In-memory cache service with TTL support"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cleanup_interval = 300  # 5 minutes
        self._start_cleanup_task()
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set cache value with TTL"""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if datetime.utcnow() > entry["expires_at"]:
            del self.cache[key]
            return None
        
        return entry["value"]
    
    def delete(self, key: str):
        """Delete cache entry"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(self.cleanup_interval)
                self.cleanup_expired()
        
        try:
            asyncio.create_task(cleanup_loop())
        except RuntimeError:
            # No event loop running, cleanup will be manual
            pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.utcnow()
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for entry in self.cache.values()
            if now > entry["expires_at"]
        )
        
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
            "memory_usage_mb": len(str(self.cache)) / (1024 * 1024)
        }

# Global cache instance
cache = CacheService()

# Cache decorators
def cache_result(prefix: str, ttl_seconds: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_data = {"args": args, "kwargs": kwargs}
            cache_key = cache._generate_key(prefix, cache_data)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result
        
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_data = {"args": args, "kwargs": kwargs}
            cache_key = cache._generate_key(prefix, cache_data)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
