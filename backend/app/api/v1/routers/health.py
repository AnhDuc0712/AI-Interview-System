from fastapi import APIRouter, Depends

from app.services.health_service import HealthService

router = APIRouter(tags=['Health'])


def get_health_service() -> HealthService:
    return HealthService()


@router.get('/health')
async def read_health(service: HealthService = Depends(get_health_service)):
    return await service.get_status()
