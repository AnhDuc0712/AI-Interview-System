from fastapi import Depends, Request
import logging
import traceback

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import AuthenticatedPrincipal, User
from app.services.clerk_auth import ClerkAuthService, get_clerk_auth_service
from app.services.user_sync import UserSyncService, get_user_sync_service

logger = logging.getLogger(__name__)


def get_auth_service() -> ClerkAuthService:
    return get_clerk_auth_service()


def get_user_sync_dependency() -> UserSyncService:
    return get_user_sync_service()


def get_optional_current_principal(
    request: Request,
    auth_service: ClerkAuthService = Depends(get_auth_service)
) -> AuthenticatedPrincipal | None:
    if getattr(request.state, 'current_principal', None) is not None:
        return request.state.current_principal

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        logger.info('No Authorization header found for %s %s', request.method, request.url.path)
        return None

    try:
        logger.debug('Attempting to verify Clerk token for %s %s', request.method, request.url.path)
        payload = auth_service.verify_request(request)
        principal = auth_service.build_principal(payload)
        logger.info(
            'Authenticated principal resolved: clerk_user_id=%s issuer=%s',
            principal.clerk_user_id,
            principal.issuer
        )
        request.state.current_principal = principal
        return principal
    except Exception as exc:
        # AuthenticationError is already logged in verify_request, but we log the failure context here too
        logger.error(
            'Authentication failed for %s %s: %s',
            request.method,
            request.url.path,
            str(exc)
        )
        raise


async def get_current_user(
    request: Request,
    principal: AuthenticatedPrincipal | None = Depends(get_optional_current_principal),
    user_sync_service: UserSyncService = Depends(get_user_sync_dependency)
) -> User:
    if principal is None:
        raise AuthenticationError('Authentication credentials were not provided')
    if getattr(request.state, 'current_user', None) is not None:
        return request.state.current_user

    try:
        user = await user_sync_service.sync_authenticated_user(principal)
    except Exception as exc:
        logger.error(
            'Failed to sync current user for clerk_user_id=%s on %s %s: %s\n%s',
            principal.clerk_user_id,
            request.method,
            request.url.path,
            exc,
            traceback.format_exc()
        )
        raise

    if user.state.is_deleted:
        raise AuthorizationError('User account is deactivated')
    logger.info(
        'Current user resolved for %s %s user_public_id=%s clerk_user_id=%s',
        request.method,
        request.url.path,
        user.public_id,
        principal.clerk_user_id
    )
    request.state.current_user = user
    return user
