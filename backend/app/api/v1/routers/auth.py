from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import CurrentUserResponse, ProtectedRouteResponse

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.get('/me', response_model=CurrentUserResponse)
async def get_current_authenticated_user(
    current_user: User = Depends(get_current_user)
) -> CurrentUserResponse:
    return CurrentUserResponse(user=current_user)


@router.get('/protected', response_model=ProtectedRouteResponse)
async def get_protected_resource(
    current_user: User = Depends(get_current_user)
) -> ProtectedRouteResponse:
    return ProtectedRouteResponse(
        message='You have access to this protected resource',
        user=current_user
    )
