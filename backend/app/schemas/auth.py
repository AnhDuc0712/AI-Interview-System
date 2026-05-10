from pydantic import BaseModel

from app.models.user import User


class CurrentUserResponse(BaseModel):
    user: User


class ProtectedRouteResponse(BaseModel):
    message: str
    user: User
