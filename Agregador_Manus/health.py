from fastapi import APIRouter, Depends
from datetime import datetime
import time
import structlog
from app.models.search import HealthCheck, APIStatus
from app.core.cache import CacheService, get_cache
from app.services.portal_transparencia import PortalTransparenciaService
from app.config import settings, API_CONFIG

logger = structlog.get_logger()
router = APIRouter()

# Tempo de início da aplicação
app_start_time = time.time()

@router.get("/health", response_model=HealthCheck)
async def health_check(cache: CacheService = Depends(get_cache)):
    """
    Verifica o status geral do sistema e das APIs
    """
    try:
        # Verifica status do cache
        cache_stats = await cache.get_stats()
        cache_status = cache_stats.get("status", "unknown")
        
        # Verifica status das APIs
        api_statuses = {}
        
        # Portal da Transparência
        try:
            portal_service = PortalTransparenciaService()
            portal_healthy = await portal_service.health_check()
            api_statuses["portal_transparencia"] = (
                APIStatus.ACTIVE if portal_healthy else APIStatus.ERROR
            )
            await portal_service.client.aclose()
        except Exception as e:
            logger.error("Portal Transparência health check failed", error=str(e))
            api_statuses["portal_transparencia"] = APIStatus.ERROR
        
        # Outras APIs (implementar conforme necessário)
        api_statuses["brasil_api"] = APIStatus.ACTIVE  # Placeholder
        api_statuses["camara_deputados"] = APIStatus.ACTIVE  # Placeholder
        api_statuses["senado_federal"] = APIStatus.ACTIVE  # Placeholder
        api_statuses["ibge"] = APIStatus.ACTIVE  # Placeholder
        api_statuses["banco_central"] = APIStatus.ACTIVE  # Placeholder
        
        # Calcula uptime
        uptime_seconds = int(time.time() - app_start_time)
        
        # Determina status geral
        all_apis_healthy = all(
            status == APIStatus.ACTIVE for status in api_statuses.values()
        )
        cache_healthy = cache_status == "connected"
        
        overall_status = "healthy" if (all_apis_healthy and cache_healthy) else "degraded"
        
        return HealthCheck(
            status=overall_status,
            timestamp=datetime.now(),
            version=settings.app_version,
            apis=api_statuses,
            cache_status=cache_status,
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        logger.error("Health check error", error=str(e))
        return HealthCheck(
            status="error",
            timestamp=datetime.now(),
            version=settings.app_version,
            apis={},
            cache_status="error",
            uptime_seconds=int(time.time() - app_start_time)
        )

@router.get("/health/cache")
async def cache_health(cache: CacheService = Depends(get_cache)):
    """
    Verifica especificamente o status do cache Redis
    """
    return await cache.get_stats()

@router.get("/health/apis")
async def apis_health():
    """
    Retorna informações detalhadas sobre todas as APIs disponíveis
    """
    apis_info = []
    
    for api_key, api_config in API_CONFIG.items():
        # Status placeholder (implementar verificação real conforme necessário)
        status = APIStatus.ACTIVE if api_config.get("enabled", True) else APIStatus.INACTIVE
        
        apis_info.append({
            "key": api_key,
            "name": api_config["name"],
            "base_url": api_config["base_url"],
            "status": status,
            "enabled": api_config.get("enabled", True),
            "token_required": api_config.get("token_required", False),
            "rate_limit": api_config.get("rate_limit", {}),
            "categories": list(api_config.get("categories", {}).keys()) if api_config.get("categories") else []
        })
    
    return {"apis": apis_info}

