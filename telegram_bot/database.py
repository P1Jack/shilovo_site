"""
МОДУЛЬ ДЛЯ РАБОТЫ С ЛОКАЛЬНОЙ БАЗОЙ ДАННЫХ

Используется для кеширования данных пользователя и участков.
"""

import time
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """Простой in-memory кеш с TTL"""
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = 300  # 5 минут
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Сохраняет значение в кеше"""
        expire_time = time.time() + (ttl or self.default_ttl)
        self._storage[key] = {
            'value': value,
            'expire_time': expire_time
        }
    
    def get(self, key: str) -> Any:
        """Получает значение из кеша"""
        if key not in self._storage:
            return None
        
        item = self._storage[key]
        
        if time.time() > item['expire_time']:
            del self._storage[key]
            return None
        
        return item['value']
    
    def delete(self, key: str) -> bool:
        """Удаляет значение из кеша"""
        if key in self._storage:
            del self._storage[key]
            return True
        return False

# Глобальные экземпляры кешей
plots_cache = SimpleCache()
user_cache = SimpleCache()
bookings_cache = SimpleCache()

def cache_plots(plots: list, ttl: int = 60) -> None:
    """Сохраняет список участков в кеш"""
    plots_cache.set('available_plots', plots, ttl=ttl)

def get_cached_plots() -> Optional[list]:
    """Получает список участков из кеша"""
    return plots_cache.get('available_plots')

def cache_user_bookings(user_id: int, bookings: list, ttl: int = 60) -> None:
    """Сохраняет брони пользователя в кеш"""
    key = f"user_{user_id}_bookings"
    bookings_cache.set(key, bookings, ttl=ttl)

def get_cached_user_bookings(user_id: int) -> Optional[list]:
    """Получает брони пользователя из кеша"""
    key = f"user_{user_id}_bookings"
    return bookings_cache.get(key)
