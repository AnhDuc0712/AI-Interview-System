from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, model_validator


class CVFileType(str, Enum):
    pdf = 'pdf'
    docx = 'docx'


class CVProcessingStatus(str, Enum):
    pending = 'pending'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'


class CVStorageProvider(str, Enum):
    local = 'local'


class StoredFileMetadata(BaseModel):
    provider: CVStorageProvider
    path: str
    filename: str
    content_type: str
    size_bytes: int
    checksum_sha256: str
    uploaded_at: datetime


class OriginalFileMetadata(BaseModel):
    original_filename: str
    content_type: str
    file_type: CVFileType
    size_bytes: int


class CVExtractionMetadata(BaseModel):
    extractor_name: str
    extractor_version: str
    extracted_at: datetime | None = None
    raw_text_length: int = 0
    normalized_text_length: int = 0


class StructuredCVPersonalInfo(BaseModel):
    name: str | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    github: str | None = None
    linkedin: str | None = None
    location: str | None = None
    summary: str | None = None

    @model_validator(mode='after')
    def sync_name_fields(self) -> 'StructuredCVPersonalInfo':
        resolved_name = self.name or self.full_name
        self.name = resolved_name
        self.full_name = resolved_name
        return self


class StructuredCVExperienceItem(BaseModel):
    title: str | None = None
    company: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    location: str | None = None
    responsibilities: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra='allow')


class StructuredCVEducationItem(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    graduation_date: str | None = None
    gpa: str | None = None

    model_config = ConfigDict(extra='allow')


class StructuredCVProjectItem(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    start_date: str | None = None
    end_date: str | None = None

    model_config = ConfigDict(extra='allow')


class StructuredCVCertificationItem(BaseModel):
    name: str | None = None
    issuer: str | None = None
    date: str | None = None

    model_config = ConfigDict(extra='allow')


class StructuredCVData(BaseModel):
    personal_info: StructuredCVPersonalInfo = Field(default_factory=StructuredCVPersonalInfo)
    skills: list[str] = Field(default_factory=list)
    experience: list[StructuredCVExperienceItem] = Field(default_factory=list)
    education: list[StructuredCVEducationItem] = Field(default_factory=list)
    projects: list[StructuredCVProjectItem] = Field(default_factory=list)
    certifications: list[StructuredCVCertificationItem] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    categorized_skills: dict[str, list[str]] = Field(default_factory=dict)
    raw_sections: dict[str, list[str]] = Field(default_factory=dict)


class CVParserMetadata(BaseModel):
    parser_name: str
    parser_version: str
    parsed_at: datetime | None = None


class CVOwnership(BaseModel):
    user_public_id: str
    user_role: str


class CVMetadata(BaseModel):
    created_at: datetime
    updated_at: datetime
    processing_started_at: datetime | None = None
    processing_completed_at: datetime | None = None
    failed_at: datetime | None = None
    last_error: str | None = None


class CVRecord(BaseModel):
    id: str | None = Field(default=None, validation_alias='_id', serialization_alias='id')
    public_id: str
    ownership: CVOwnership
    status: CVProcessingStatus
    original_file: OriginalFileMetadata
    stored_file: StoredFileMetadata
    extraction: CVExtractionMetadata
    parser: CVParserMetadata
    normalized_content: StructuredCVData | None = None
    normalized_text: str | None = None
    metadata: CVMetadata

    model_config = ConfigDict(populate_by_name=True)
