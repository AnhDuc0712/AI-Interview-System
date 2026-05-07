from app.db.client import db


class HealthRepository:
    async def ping(self) -> bool:
        try:
            await db.command('ping')
            return True
        except Exception:
            return False
