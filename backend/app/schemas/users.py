from pydantic import BaseModel, Field, field_validator

from app.models.user import User, UserProfile


class UpdateMyProfileRequest(BaseModel):
    headline: str | None = Field(default=None, max_length=120)
    biography: str | None = Field(default=None, max_length=2000)
    location: str | None = Field(default=None, max_length=120)
    timezone: str | None = Field(default=None, max_length=80)
    target_role: str | None = Field(default=None, max_length=120)
    years_of_experience: int | None = Field(default=None, ge=0, le=60)
    skills: list[str] | None = Field(default=None, max_length=20)
    preferences: dict[str, str] | None = None

    @field_validator('headline', 'biography', 'location', 'timezone', 'target_role')
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator('skills')
    @classmethod
    def normalize_skills(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None

        normalized: list[str] = []
        seen: set[str] = set()
        for skill in value:
            stripped = skill.strip()
            if not stripped:
                continue
            key = stripped.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(stripped)

        if len(normalized) > 20:
            raise ValueError('Skills cannot contain more than 20 unique items')
        return normalized

    @field_validator('preferences')
    @classmethod
    def normalize_preferences(
        cls,
        value: dict[str, str] | None
    ) -> dict[str, str] | None:
        if value is None:
            return None

        normalized: dict[str, str] = {}
        for key, raw_value in value.items():
            normalized_key = key.strip()
            normalized_value = raw_value.strip()
            if not normalized_key or not normalized_value:
                continue
            normalized[normalized_key] = normalized_value
        return normalized


class UserProfileResponse(BaseModel):
    user: User
    profile_completion: 'ProfileCompletionSummary'


class UpdateMyProfileResponse(BaseModel):
    user: User
    profile_completion: 'ProfileCompletionSummary'


class ProfileCompletionSummary(BaseModel):
    score: int
    fields_completed: int
    fields_total: int
    is_complete: bool


class AppManagedProfileSnapshot(BaseModel):
    public_id: str
    role: str
    profile: UserProfile
    profile_completion: ProfileCompletionSummary


UserProfileResponse.model_rebuild()
UpdateMyProfileResponse.model_rebuild()
