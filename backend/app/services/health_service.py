from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, repository: HealthRepository | None = None) -> None:
        self.repository = repository or HealthRepository()

    async def get_status(self) -> dict:
        connected = await self.repository.ping()
        return {
            'status': 'ok' if connected else 'error',
            'database': connected
        }
