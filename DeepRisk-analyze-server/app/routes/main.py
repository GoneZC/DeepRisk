from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def index():
    """首页"""
    return {"message": "欢迎使用SmartRisk分析服务"}

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

@router.get("/actuator/health")
async def nacos_health_check():
    """Nacos健康检查接口"""
    return {"status": "UP"}