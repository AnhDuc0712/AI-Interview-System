from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.dependencies.auth import get_current_user
from app.dependencies.cv import get_cv_ingestion_dependency, get_cv_query_dependency
from app.main import app
from app.models.cv import (
    CVExtractionMetadata,
    CVFileType,
    CVMetadata,
    CVOwnership,
    CVParserMetadata,
    CVProcessingStatus,
    CVRecord,
    CVStorageProvider,
    OriginalFileMetadata,
    StoredFileMetadata,
    StructuredCVData,
    StructuredCVPersonalInfo,
)
from app.models.user import (
    ClerkManagedUserData,
    ClerkProfile,
    User,
    UserMetadata,
    UserProfile,
    UserRole,
    UserState,
)
from app.services.cv_ingestion import CVIngestionService
from app.services.cv_query import CVQueryService


def _build_user() -> User:
    return User(
        _id='507f1f77bcf86cd799439011',
        public_id='usr_candidate_1',
        role=UserRole.candidate,
        clerk=ClerkManagedUserData(
            clerk_user_id='user_candidate_1',
            email='candidate@example.com',
            issuer='https://example.clerk.accounts.dev',
            profile=ClerkProfile(
                first_name='CV',
                last_name='Owner',
                full_name='CV Owner',
                username='cv.owner',
                image_url='https://example.com/cv-owner.png'
            )
        ),
        profile=UserProfile(),
        metadata=UserMetadata(
            created_at='2026-05-08T00:00:00Z',
            updated_at='2026-05-08T00:00:00Z',
            last_sign_in_at='2026-05-08T00:00:00Z',
            clerk_synced_at='2026-05-08T00:00:00Z'
        ),
        state=UserState(is_deleted=False, deleted_at=None)
    )


class FakeCVIngestionService(CVIngestionService):
    async def ensure_ready(self) -> None:
        return None

    async def upload_cv(self, *, user: User, upload_file):
        now = datetime.now(timezone.utc)
        return CVRecord(
            _id='507f1f77bcf86cd799439099',
            public_id='cv_test_1',
            ownership=CVOwnership(
                user_public_id=user.public_id,
                user_role=user.role.value
            ),
            status=CVProcessingStatus.completed,
            original_file=OriginalFileMetadata(
                original_filename=upload_file.filename or 'resume.pdf',
                content_type=upload_file.content_type or 'application/pdf',
                file_type=CVFileType.pdf,
                size_bytes=128
            ),
            stored_file=StoredFileMetadata(
                provider=CVStorageProvider.local,
                path='usr_candidate_1/cv_test_1/resume.pdf',
                filename='resume.pdf',
                content_type='application/pdf',
                size_bytes=128,
                checksum_sha256='abc123',
                uploaded_at=now
            ),
            extraction=CVExtractionMetadata(
                extractor_name='pypdf',
                extractor_version='1.0',
                extracted_at=now,
                raw_text_length=240,
                normalized_text_length=220
            ),
            parser=CVParserMetadata(
                parser_name='rule-based-structured-cv-parser',
                parser_version='v1',
                parsed_at=now
            ),
            normalized_content=StructuredCVData(
                personal_info=StructuredCVPersonalInfo(
                    full_name='CV Owner',
                    email='candidate@example.com'
                ),
                skills=['Python', 'FastAPI']
            ),
            normalized_text='CV Owner\nPython\nFastAPI',
            metadata=CVMetadata(
                created_at=now,
                updated_at=now,
                processing_started_at=now,
                processing_completed_at=now
            )
        )


class FakeCVQueryService(CVQueryService):
    async def list_my_cvs(self, *, user: User, page: int, limit: int, status=None):
        record = await FakeCVIngestionService().upload_cv(
            user=user,
            upload_file=type(
                'UploadStub',
                (),
                {'filename': 'resume.pdf', 'content_type': 'application/pdf'}
            )()
        )
        from app.schemas.cv import CVListResponse, PaginationMeta

        items = [record]
        if status is not None:
            items = [item for item in items if item.status == status]
        return CVListResponse(
            items=items,
            pagination=PaginationMeta(page=page, limit=limit, total=len(items), total_pages=1)
        )

    async def get_my_cv_detail(self, *, user: User, public_id: str):
        record = await FakeCVIngestionService().upload_cv(
            user=user,
            upload_file=type(
                'UploadStub',
                (),
                {'filename': 'resume.pdf', 'content_type': 'application/pdf'}
            )()
        )
        return record.model_copy(update={'public_id': public_id})


async def _override_current_user() -> User:
    return _build_user()


def _override_cv_ingestion_service() -> CVIngestionService:
    return FakeCVIngestionService()


def _override_cv_query_service() -> CVQueryService:
    return FakeCVQueryService()


def test_cv_upload_endpoint_returns_owned_record():
    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_cv_ingestion_dependency] = _override_cv_ingestion_service
    client = TestClient(app)

    response = client.post(
        '/api/v1/cvs/upload',
        files={'file': ('resume.pdf', b'%PDF-1.4 test', 'application/pdf')}
    )

    assert response.status_code == 200
    body = response.json()
    assert body['cv']['public_id'] == 'cv_test_1'
    assert body['cv']['ownership']['user_public_id'] == 'usr_candidate_1'
    assert body['cv']['status'] == 'completed'
    assert body['cv']['parser']['parser_version'] == 'v1'

    app.dependency_overrides.clear()


def test_list_my_cvs_returns_paginated_records():
    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_cv_query_dependency] = _override_cv_query_service
    client = TestClient(app)

    response = client.get('/api/v1/cvs/me?page=1&limit=10')

    assert response.status_code == 200
    body = response.json()
    assert body['pagination']['page'] == 1
    assert body['pagination']['total'] == 1
    assert body['items'][0]['ownership']['user_public_id'] == 'usr_candidate_1'

    app.dependency_overrides.clear()


def test_get_cv_detail_returns_structured_cv():
    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_cv_query_dependency] = _override_cv_query_service
    client = TestClient(app)

    response = client.get('/api/v1/cvs/cv_detail_1')

    assert response.status_code == 200
    body = response.json()
    assert body['cv']['public_id'] == 'cv_detail_1'
    assert body['cv']['normalized_content']['skills'] == ['Python', 'FastAPI']

    app.dependency_overrides.clear()
