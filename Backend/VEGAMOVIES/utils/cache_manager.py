"""
Cache Manager - Intelligent caching system for Vegamovies data
Handles data persistence and retrieval with TTL support
"""

import json
import time
import os
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

class CacheManager:
    """Manages caching of Vegamovies data with TTL and cleanup"""
    
    def __init__(self, cache_dir: str = None):
        # Set cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            project_root = Path(__file__).resolve().parents[3]
            self.cache_dir = project_root / "Backend" / "VEGAMOVIES" / "data"
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "vegamovies_cache.json"
        
        # Load existing cache
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache data from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"[CacheManager] Loaded cache with {len(data)} entries")
                    return data
        except Exception as e:
            print(f"[CacheManager] Error loading cache: {e}")
        
        return {}
    
    def _save_cache(self):
        """Save cache data to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            print(f"[CacheManager] Saved cache with {len(self.cache_data)} entries")
        except Exception as e:
            print(f"[CacheManager] Error saving cache: {e}")
    
    def _is_expired(self, entry: Dict) -> bool:
        """Check if cache entry is expired"""
        try:
            expires_at = entry.get('expires_at', 0)
            return time.time() > expires_at
        except Exception:
            return True
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cache entry with TTL (time to live in seconds)"""
        try:
            expires_at = time.time() + ttl
            
            self.cache_data[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': expires_at,
                'ttl': ttl
            }
            
            self._save_cache()
            print(f"[CacheManager] Cached '{key}' with TTL {ttl}s")
            
        except Exception as e:
            print(f"[CacheManager] Error setting cache for '{key}': {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache entry if not expired"""
        try:
            if key not in self.cache_data:
                return None
            
            entry = self.cache_data[key]
            
            if self._is_expired(entry):
                print(f"[CacheManager] Cache expired for '{key}'")
                del self.cache_data[key]
                self._save_cache()
                return None
            
            print(f"[CacheManager] Cache hit for '{key}'")
            return entry['value']
            
        except Exception as e:
            print(f"[CacheManager] Error getting cache for '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        try:
            if key in self.cache_data:
                del self.cache_data[key]
                self._save_cache()
                print(f"[CacheManager] Deleted cache for '{key}'")
                return True
            return False
        except Exception as e:
            print(f"[CacheManager] Error deleting cache for '{key}': {e}")
            return False
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries"""
        expired_keys = []
        
        try:
            for key, entry in self.cache_data.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache_data[key]
            
            if expired_keys:
                self._save_cache()
                print(f"[CacheManager] Cleared {len(expired_keys)} expired entries")
            
            return len(expired_keys)
            
        except Exception as e:
            print(f"[CacheManager] Error clearing expired cache: {e}")
            return 0
    
    def clear_all(self):
        """Clear all cache entries"""
        try:
            count = len(self.cache_data)
            self.cache_data.clear()
            self._save_cache()
            print(f"[CacheManager] Cleared all {count} cache entries")
        except Exception as e:
            print(f"[CacheManager] Error clearing all cache: {e}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            total_entries = len(self.cache_data)
            expired_count = 0
            total_size = 0
            
            for key, entry in self.cache_data.items():
                if self._is_expired(entry):
                    expired_count += 1
                
                # Estimate size
                try:
                    entry_str = json.dumps(entry)
                    total_size += len(entry_str.encode('utf-8'))
                except Exception:
                    pass
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_count,
                'active_entries': total_entries - expired_count,
                'estimated_size_bytes': total_size,
                'cache_file': str(self.cache_file)
            }
            
        except Exception as e:
            print(f"[CacheManager] Error getting stats: {e}")
            return {}
    
    def cleanup_old_entries(self, max_age_days: int = 7):
        """Remove entries older than specified days"""
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        old_keys = []
        
        try:
            for key, entry in self.cache_data.items():
                created_at = entry.get('created_at', 0)
                if created_at < cutoff_time:
                    old_keys.append(key)
            
            for key in old_keys:
                del self.cache_data[key]
            
            if old_keys:
                self._save_cache()
                print(f"[CacheManager] Cleaned up {len(old_keys)} old entries")
            
            return len(old_keys)
            
        except Exception as e:
            print(f"[CacheManager] Error during cleanup: {e}")
            return 0
    
    def has_key(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        return self.get(key) is not None
    
    def get_keys(self) -> list:
        """Get all active (non-expired) cache keys"""
        active_keys = []
        
        try:
            for key, entry in self.cache_data.items():
                if not self._is_expired(entry):
                    active_keys.append(key)
            
            return active_keys
            
        except Exception as e:
            print(f"[CacheManager] Error getting keys: {e}")
            return []
    
    def refresh_ttl(self, key: str, new_ttl: int = 3600) -> bool:
        """Refresh TTL for existing cache entry"""
        try:
            if key in self.cache_data:
                entry = self.cache_data[key]
                if not self._is_expired(entry):
                    entry['expires_at'] = time.time() + new_ttl
                    entry['ttl'] = new_ttl
                    self._save_cache()
                    print(f"[CacheManager] Refreshed TTL for '{key}' to {new_ttl}s")
                    return True
            
            return False
            
        except Exception as e:
            print(f"[CacheManager] Error refreshing TTL for '{key}': {e}")
            return False
