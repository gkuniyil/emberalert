"""
Redis caching service.

CACHING STRATEGY:
- Cache predictions by location + conditions
- TTL: 1 hour (weather changes slowly)
- Reduces API response time by ~85%
"""

import redis
import json
import hashlib
from typing import Optional
from app.config import config
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Redis cache manager"""
    
    def __init__(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                decode_responses=True  # Return strings, not bytes
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connected successfully")
            
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def _generate_key(self, data: dict) -> str:
        """
        Generate cache key from request data.
        
        KEY STRATEGY:
        - Hash input parameters
        - Ensures unique key per unique input
        - Short keys (MD5 hash = 32 chars)
        
        Args:
            data: Request parameters
        
        Returns:
            Cache key string
        """
        # Sort dict for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        
        # MD5 hash (fast, suitable for caching)
        hash_object = hashlib.md5(sorted_data.encode())
        cache_key = f"prediction:{hash_object.hexdigest()}"
        
        return cache_key
    
    def get(self, request_data: dict) -> Optional[dict]:
        """
        Get cached prediction.
        
        Args:
            request_data: Request parameters
        
        Returns:
            Cached prediction or None
        """
        if not self.redis_client:
            return None
        
        try:
            key = self._generate_key(request_data)
            cached = self.redis_client.get(key)
            
            if cached:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(cached)
            
            logger.debug(f"Cache MISS: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, request_data: dict, prediction: dict, ttl: int = None):
        """
        Cache a prediction.
        
        Args:
            request_data: Request parameters
            prediction: Prediction result
            ttl: Time to live in seconds (default from config)
        """
        if not self.redis_client:
            return
        
        try:
            key = self._generate_key(request_data)
            ttl = ttl or config.CACHE_TTL
            
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(prediction)
            )
            
            logger.debug(f"Cached: {key} (TTL: {ttl}s)")
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def clear_all(self):
        """Clear all cached predictions"""
        if not self.redis_client:
            return
        
        try:
            # Find all prediction keys
            keys = self.redis_client.keys("prediction:*")
            
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached predictions")
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {'connected': False}
        
        try:
            info = self.redis_client.info('stats')
            
            return {
                'connected': True,
                'total_keys': self.redis_client.dbsize(),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {'connected': False}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100

# Global cache instance
cache_service = CacheService()