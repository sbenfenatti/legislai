import redis.asyncio as redis
import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import structlog
from app.config import settings

logger = structlog.get_logger()

class CacheService:
    """Serviço de cache Redis"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.connected = False
    
    async def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Testa a conexão
            await self.redis.ping()
            self.connected = True
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            self.connected = False
            raise
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis:
            await self.redis.close()
            self.connected = False
            logger.info("Redis disconnected")
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Gera chave única para cache baseada nos parâmetros"""
        # Ordena os parâmetros para garantir consistência
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True, default=str)
        
        # Gera hash MD5 dos parâmetros
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        return f"{prefix}:{params_hash}"
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera dados do cache"""
        if not self.connected or not self.redis:
            return None
        
        try:
            data = await self.redis.get(key)
            if data:
                result = json.loads(data)
                logger.debug("Cache hit", key=key)
                return result
            else:
                logger.debug("Cache miss", key=key)
                return None
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None
    
    async def set(
        self, 
        key: str, 
        value: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> bool:
        """Armazena dados no cache"""
        if not self.connected or not self.redis:
            return False
        
        try:
            ttl = ttl or settings.cache_ttl
            data = json.dumps(value, default=str)
            
            await self.redis.setex(key, ttl, data)
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove dados do cache"""
        if not self.connected or not self.redis:
            return False
        
        try:
            result = await self.redis.delete(key)
            logger.debug("Cache delete", key=key, deleted=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Remove todas as chaves que correspondem ao padrão"""
        if not self.connected or not self.redis:
            return 0
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info("Cache pattern cleared", pattern=pattern, deleted=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.error("Cache clear pattern error", pattern=pattern, error=str(e))
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        if not self.connected or not self.redis:
            return {"status": "disconnected"}
        
        try:
            info = await self.redis.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            logger.error("Cache stats error", error=str(e))
            return {"status": "error", "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calcula taxa de acerto do cache"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

# Instância global do cache
cache_service = CacheService()

async def get_cache() -> CacheService:
    """Dependency para injeção do cache"""
    return cache_service

