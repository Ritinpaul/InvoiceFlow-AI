"""Redis caching layer for performance optimization"""
import redis
import json
import os
from typing import Optional, Dict, Any

class CacheManager:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600
        
    def cache_vendor(self, vendor_name: str, is_approved: bool, ttl: int = 86400):
        """Cache vendor approval status"""
        key = f"vendor:{vendor_name.lower()}"
        self.redis_client.setex(key, ttl, json.dumps({"approved": is_approved}))
        
    def get_cached_vendor(self, vendor_name: str) -> Optional[bool]:
        """Get cached vendor"""
        key = f"vendor:{vendor_name.lower()}"
        data = self.redis_client.get(key)
        return json.loads(data)["approved"] if data else None
    
    def cache_invoice(self, invoice_number: str, invoice_data: Dict[str, Any], ttl: int = 2592000):
        """Cache invoice for duplicate detection"""
        key = f"invoice:{invoice_number}"
        self.redis_client.setex(key, ttl, json.dumps(invoice_data))
        
    def get_cached_invoice(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get cached invoice"""
        key = f"invoice:{invoice_number}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    def cache_stats(self, stats: Dict[str, Any], ttl: int = 300):
        """Cache dashboard stats"""
        self.redis_client.setex("stats:dashboard", ttl, json.dumps(stats))
        
    def get_cached_stats(self) -> Optional[Dict[str, Any]]:
        """Get cached stats"""
        data = self.redis_client.get("stats:dashboard")
        return json.loads(data) if data else None
    
    def invalidate_stats(self):
        """Clear stats cache"""
        self.redis_client.delete("stats:dashboard")
    
    def check_rate_limit(self, client_id: str, max_requests: int = 100, window: int = 3600) -> bool:
        """Rate limiting"""
        key = f"ratelimit:{client_id}"
        current = self.redis_client.get(key)
        
        if current is None:
            self.redis_client.setex(key, window, 1)
            return True
        
        if int(current) >= max_requests:
            return False
        
        self.redis_client.incr(key)
        return True
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        info = self.redis_client.info("stats")
        return {
            "total_keys": self.redis_client.dbsize(),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "memory_used": info.get("used_memory_human", "0"),
        }
    
    def flush_all(self):
        """Clear all cache"""
        self.redis_client.flushdb()

cache = CacheManager()
