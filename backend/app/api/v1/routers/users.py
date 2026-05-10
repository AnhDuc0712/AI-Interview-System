from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.users import get_user_profile_dependency
from app.models.user import User
from app.schemas.users import (
    UpdateMyProfileRequest,
    UpdateMyProfileResponse,
    UserProfileResponse,
)
from app.services.user_profile import UserProfileService

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/me/profile', response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    user_profile_service: UserProfileService = Depends(get_user_profile_dependency)
) -> UserProfileResponse:
    user = await user_profile_service.get_my_profile(current_user)
    return UserProfileResponse(
        user=user,
        profile_completion=user_profile_service.build_profile_completion(user)
    )


@router.patch('/me', response_model=UpdateMyProfileResponse)
async def update_my_profile(
    payload: UpdateMyProfileRequest,
    current_user: User = Depends(get_current_user),
    user_profile_service: UserProfileService = Depends(get_user_profile_dependency)
) -> UpdateMyProfileResponse:
    user = await user_profile_service.update_my_profile(current_user, payload)
    return UpdateMyProfileResponse(
        user=user,
        profile_completion=user_profile_service.build_profile_completion(user)
    )
