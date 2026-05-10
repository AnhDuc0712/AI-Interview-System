from app.services.user_profile import UserProfileService, get_user_profile_service


def get_user_profile_dependency() -> UserProfileService:
    return get_user_profile_service()
