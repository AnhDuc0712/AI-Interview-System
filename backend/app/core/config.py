import base64
import binascii
from pathlib import Path

from pydantic import AliasChoices, AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    app_name: str = 'AI Interview System API'
    mongodb_uri: str = Field(
        default='mongodb://localhost:27017/ai_interview_system',
        validation_alias=AliasChoices('MONGODB_URI', 'MONGO_URL')
    )
    mongodb_db_name: str = Field(
        default='ai_interview_system',
        validation_alias='MONGODB_DB_NAME'
    )
    allowed_origins: list[str] = [
        'http://localhost:4173',
        'http://127.0.0.1:4173',
        'http://192.168.1.41:4173',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:8000',
        'http://192.168.1.31:4173'
    ]
    clerk_publishable_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices('CLERK_PUBLISHABLE_KEY', 'VITE_CLERK_PUBLISHABLE_KEY')
    )
    clerk_frontend_api: str | None = Field(
        default=None,
        validation_alias=AliasChoices('CLERK_FRONTEND_API', 'VITE_CLERK_FRONTEND_API')
    )
    clerk_secret_key: str | None = Field(default=None, validation_alias='CLERK_SECRET_KEY')
    clerk_jwt_issuer: str | None = Field(default=None, validation_alias='CLERK_JWT_ISSUER')
    clerk_jwt_audience: str | None = Field(default=None, validation_alias='CLERK_JWT_AUDIENCE')
    clerk_jwks_url: str | None = Field(default=None, validation_alias='CLERK_JWKS_URL')
    playwright_headless: bool = Field(default=True, validation_alias='PLAYWRIGHT_HEADLESS')
    playwright_timeout_ms: int = Field(default=30000, validation_alias='PLAYWRIGHT_TIMEOUT_MS')
    playwright_user_agent: str | None = Field(
        default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        validation_alias='PLAYWRIGHT_USER_AGENT'
    )
    crawler_rate_limit_seconds: float = Field(default=1.0, validation_alias='CRAWLER_RATE_LIMIT_SECONDS')
    crawler_max_retries: int = Field(default=2, validation_alias='CRAWLER_MAX_RETRIES')
    clerk_authorized_parties: str | None = Field(
        default=None,
        validation_alias='CLERK_AUTHORIZED_PARTIES'
    )
    cv_upload_dir: str = Field(default='storage/cvs', validation_alias='CV_UPLOAD_DIR')
    cv_max_file_size_bytes: int = Field(
        default=5 * 1024 * 1024,
        validation_alias='CV_MAX_FILE_SIZE_BYTES'
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=(PROJECT_ROOT / '.env', BASE_DIR / '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    @property
    def resolved_clerk_frontend_api(self) -> str | None:
        decoded_frontend_api = _extract_clerk_frontend_api_from_publishable_key(self.clerk_publishable_key)
        if self.clerk_frontend_api:
            normalized_frontend_api = (
                self.clerk_frontend_api.replace('https://', '').replace('http://', '').rstrip('/')
            )
            if normalized_frontend_api != 'clerk.example.com':
                return normalized_frontend_api
        return decoded_frontend_api

    @property
    def resolved_clerk_jwt_issuer(self) -> str | None:
        if self.clerk_jwt_issuer:
            return self.clerk_jwt_issuer.rstrip('/')
        if self.resolved_clerk_frontend_api:
            return f'https://{self.resolved_clerk_frontend_api}'
        return None

    @property
    def resolved_clerk_issuers(self) -> list[str]:
        issuers: list[str] = []
        if self.clerk_jwt_issuer:
            issuers.append(self.clerk_jwt_issuer)
        if self.resolved_clerk_frontend_api:
            issuers.append(f'https://{self.resolved_clerk_frontend_api}')

        normalized: list[str] = []
        for issuer in issuers:
            stripped = issuer.rstrip('/')
            if stripped and stripped not in normalized:
                normalized.append(stripped)
        return normalized

    @property
    def resolved_clerk_authorized_parties(self) -> list[str]:
        if self.clerk_authorized_parties:
            return [
                party.strip().rstrip('/')
                for party in self.clerk_authorized_parties.split(',')
                if party.strip()
            ]

        return [
            origin.rstrip('/')
            for origin in self.allowed_origins
            if ':8000' not in origin
        ]

    @property
    def resolved_clerk_jwks_url(self) -> str | None:
        if self.clerk_jwks_url:
            return self.clerk_jwks_url
        if self.resolved_clerk_jwt_issuer:
            return f'{self.resolved_clerk_jwt_issuer}/.well-known/jwks.json'
        return None


settings = Settings()


def _extract_clerk_frontend_api_from_publishable_key(publishable_key: str | None) -> str | None:
    if not publishable_key:
        return None

    encoded_value = publishable_key.split('_', 2)[-1]
    padded_value = encoded_value + '=' * (-len(encoded_value) % 4)

    try:
        decoded_value = base64.urlsafe_b64decode(padded_value.encode('utf-8')).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError):
        return None

    frontend_api = decoded_value.split('$', 1)[0].strip().rstrip('/')
    return frontend_api or None
