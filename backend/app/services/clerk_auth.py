import logging
import traceback
from typing import Any

import jwt
from fastapi import Request

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConfigurationError
from app.models.user import AuthenticatedPrincipal
from app.utils.auth import extract_bearer_token

logger = logging.getLogger(__name__)

# Cache for JWK Client to avoid fetching JWKS on every request
_jwk_clients: dict[str, jwt.PyJWKClient] = {}


def get_jwk_client(jwks_url: str) -> jwt.PyJWKClient:
    """
    Get or create a JWK client for the given JWKS URL.
    """
    if jwks_url not in _jwk_clients:
        _jwk_clients[jwks_url] = jwt.PyJWKClient(jwks_url)
    return _jwk_clients[jwks_url]


class ClerkAuthService:
    def __init__(
        self,
        authorized_parties: list[str] | None = None
    ) -> None:
        self.authorized_parties = [
            party.rstrip('/') for party in (authorized_parties or []) if party.rstrip('/')
        ]

    def verify_request(self, request: Request) -> dict[str, Any]:
        """
        Verify the Clerk JWT from the request Authorization header using JWKS.
        """
        auth_header = request.headers.get('Authorization')
        token = extract_bearer_token(auth_header)
        
        if not token:
            logger.warning('No bearer token found in Authorization header for %s %s', request.method, request.url.path)
            raise AuthenticationError('Authentication credentials were not provided')

        jwks_url = settings.resolved_clerk_jwks_url
        if not jwks_url:
            logger.error('Missing Clerk JWKS URL configuration. Check CLERK_JWT_ISSUER or CLERK_JWKS_URL.')
            raise ConfigurationError('Missing Clerk JWKS URL configuration')

        try:
            # JWKS Verification (Standard Clerk Practice)
            jwk_client = get_jwk_client(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            
            # Clerk issuers to check against
            valid_issuers = settings.resolved_clerk_issuers
            
            logger.debug('Verifying token: jwks_url=%s valid_issuers=%s', jwks_url, valid_issuers)
            
            # Decode and verify using PyJWT
            # Note: We use RS256 as Clerk uses asymmetric keys for session tokens.
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={
                    "verify_aud": bool(settings.clerk_jwt_audience),
                    "verify_iss": bool(valid_issuers),
                    "verify_iat": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                },
                issuer=valid_issuers if valid_issuers else None,
                audience=settings.clerk_jwt_audience,
                leeway=60,  # 60 seconds leeway to handle clock skew (prevents ExpiredSignatureError giả)
            )
            
            # Verify Authorized Party (azp) if provided
            azp = payload.get('azp')
            if self.authorized_parties and azp:
                if azp.rstrip('/') not in self.authorized_parties:
                    logger.warning(
                        'Token azp (%s) not in authorized parties (%s). Proceeding but logging discrepancy.', 
                        azp, self.authorized_parties
                    )
            
            logger.info('Clerk token verified successfully via JWKS. sub=%s issuer=%s', payload.get('sub'), payload.get('iss'))
            return payload

        except jwt.ExpiredSignatureError as exc:
            logger.error('Clerk token expired: %s', exc)
            raise AuthenticationError('Authentication token has expired') from exc
        except jwt.InvalidIssuerError as exc:
            logger.error('Invalid Clerk token issuer: %s. Expected one of: %s', exc, valid_issuers)
            raise AuthenticationError('Invalid authentication token issuer') from exc
        except jwt.InvalidAudienceError as exc:
            logger.error('Invalid Clerk token audience: %s. Expected: %s', exc, settings.clerk_jwt_audience)
            raise AuthenticationError('Invalid authentication token audience') from exc
        except jwt.InvalidTokenError as exc:
            logger.error('Invalid Clerk token: %s', exc)
            raise AuthenticationError('Invalid or expired authentication token') from exc
        except Exception as exc:
            logger.error('Unexpected error during Clerk token verification: %s\n%s', exc, traceback.format_exc())
            raise AuthenticationError('Unable to verify authentication token') from exc

    def build_principal(self, payload: dict[str, Any]) -> AuthenticatedPrincipal:
        """
        Build an AuthenticatedPrincipal from the verified JWT payload.
        """
        subject = payload.get('sub')
        if not isinstance(subject, str) or not subject:
            raise AuthenticationError('Token payload is missing a valid subject (sub)')

        return AuthenticatedPrincipal(
            clerk_user_id=subject,
            session_id=_string_or_none(payload.get('sid')),
            email=_string_or_none(payload.get('email')) or _string_or_none(payload.get('email_address')),
            first_name=_string_or_none(payload.get('first_name')),
            last_name=_string_or_none(payload.get('last_name')),
            full_name=_string_or_none(payload.get('name')) or _string_or_none(payload.get('full_name')),
            username=_string_or_none(payload.get('username')),
            image_url=_string_or_none(payload.get('image_url')),
            issuer=_string_or_none(payload.get('iss')),
            audience=_audience_value(payload.get('aud'))
        )


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _audience_value(value: Any) -> str | list[str] | None:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, list):
        cleaned = [item for item in value if isinstance(item, str) and item]
        return cleaned or None
    return None


def get_clerk_auth_service() -> ClerkAuthService:
    return ClerkAuthService(
        authorized_parties=settings.resolved_clerk_authorized_parties
    )
