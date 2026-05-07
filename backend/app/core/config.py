from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'AI Interview System API'
    mongodb_uri: str = Field(
        'mongodb://localhost:27017/ai_interview_system',
        env='MONGODB_URI'
    )
    allowed_origins: list[AnyHttpUrl] = [
        'http://localhost:4173',
        'http://localhost:5173',
        'http://localhost:8000'
    ]
    clerk_publishable_key: str | None = None
    clerk_secret_key: str | None = None

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
