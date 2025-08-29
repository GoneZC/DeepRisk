from fastapi import APIRouter
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "analysis-service",
        "timestamp": time.time()
    }

@router.get("/actuator/health")
async def nacos_health_check():
    """Nacos健康检查接口"""
    return {"status": "UP"}