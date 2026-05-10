from fastapi import APIRouter, Depends, File, Path, Query, UploadFile

from app.dependencies.auth import get_current_user
from app.dependencies.cv import get_cv_ingestion_dependency, get_cv_query_dependency
from app.models.cv import CVProcessingStatus
from app.models.user import User
from app.schemas.cv import CVListResponse, CVUploadResponse, StructuredCVResponse
from app.services.cv_ingestion import CVIngestionService
from app.services.cv_query import CVQueryService

router = APIRouter(prefix='/cvs', tags=['CVs'])


@router.post('/upload', response_model=CVUploadResponse)
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    cv_ingestion_service: CVIngestionService = Depends(get_cv_ingestion_dependency)
) -> CVUploadResponse:
    cv_record = await cv_ingestion_service.upload_cv(user=current_user, upload_file=file)
    return CVUploadResponse(cv=cv_record)


@router.get('/me', response_model=CVListResponse)
async def list_my_cvs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    status: CVProcessingStatus | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    cv_query_service: CVQueryService = Depends(get_cv_query_dependency)
) -> CVListResponse:
    return await cv_query_service.list_my_cvs(
        user=current_user,
        page=page,
        limit=limit,
        status=status
    )


@router.get('/{public_id}', response_model=StructuredCVResponse)
async def get_cv_detail(
    public_id: str = Path(..., min_length=3),
    current_user: User = Depends(get_current_user),
    cv_query_service: CVQueryService = Depends(get_cv_query_dependency)
) -> StructuredCVResponse:
    cv = await cv_query_service.get_my_cv_detail(
        user=current_user,
        public_id=public_id
    )
    return StructuredCVResponse(cv=cv)
