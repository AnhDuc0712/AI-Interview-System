from pydantic import BaseModel, Field

from app.models.cv import CVRecord, StructuredCVData
from app.models.cv import CVProcessingStatus


class StructuredCVResponse(BaseModel):
    cv: CVRecord


class CVUploadResponse(BaseModel):
    cv: CVRecord


class ParsedCVPreview(BaseModel):
    parsed: StructuredCVData


class CVListQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=50)
    status: CVProcessingStatus | None = None


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class CVListResponse(BaseModel):
    items: list[CVRecord]
    pagination: PaginationMeta
