from functools import lru_cache

from fastapi import UploadFile

from app.core.exceptions import ProcessingError
from app.models.cv import (
    CVExtractionMetadata,
    CVOwnership,
    OriginalFileMetadata,
)
from app.models.user import User
from app.repositories.cv_repository import CVRepository
from app.services.cv_parser import StructuredCVParserService
from app.services.document_extractor import DocumentExtractionService
from app.services.file_storage import LocalFileStorageService
from app.services.text_normalizer import TextNormalizationService
from app.services.upload_validation import UploadValidationService
from app.utils.ids import generate_public_id


class CVIngestionService:
    def __init__(
        self,
        repository: CVRepository | None = None,
        storage_service: LocalFileStorageService | None = None,
        extraction_service: DocumentExtractionService | None = None,
        normalization_service: TextNormalizationService | None = None,
        parser_service: StructuredCVParserService | None = None,
        validation_service: UploadValidationService | None = None
    ) -> None:
        self.repository = repository or CVRepository()
        self.storage_service = storage_service or LocalFileStorageService()
        self.extraction_service = extraction_service or DocumentExtractionService()
        self.normalization_service = normalization_service or TextNormalizationService()
        self.parser_service = parser_service or StructuredCVParserService()
        self.validation_service = validation_service or UploadValidationService()

    async def ensure_ready(self) -> None:
        await self.repository.ensure_indexes()
        await self.storage_service.ensure_ready()

    async def upload_cv(self, *, user: User, upload_file: UploadFile):
        filename, file_type = self.validation_service.validate_filename(upload_file.filename)
        content_type = self.validation_service.validate_content_type(upload_file, file_type)
        content = await upload_file.read()
        self.validation_service.validate_size(len(content))
        self.validation_service.validate_signature(content, file_type)

        ownership = CVOwnership(
            user_public_id=user.public_id,
            user_role=user.role.value
        )
        cv_public_id = generate_public_id(prefix='cv')
        stored_result = await self.storage_service.save(
            owner_public_id=user.public_id,
            cv_public_id=cv_public_id,
            filename=filename,
            content_type=content_type,
            content=content
        )
        record_document = await self.repository.create_pending(
            public_id=cv_public_id,
            ownership=ownership,
            original_file=OriginalFileMetadata(
                original_filename=filename,
                content_type=content_type,
                file_type=file_type,
                size_bytes=len(content)
            ),
            stored_file=stored_result.metadata
        )
        record = self.repository.deserialize(record_document)

        try:
            await self.repository.mark_processing(record.public_id)
            text, extractor_name, extractor_version = await self.extraction_service.extract_text(
                file_type,
                content
            )
            normalized_text = self.normalization_service.normalize(text)
            parsed_content, parser_metadata = self.parser_service.parse(normalized_text)
            extraction_metadata = CVExtractionMetadata(
                extractor_name=extractor_name,
                extractor_version=extractor_version,
                extracted_at=parser_metadata.parsed_at,
                raw_text_length=len(text),
                normalized_text_length=len(normalized_text)
            )
            completed_document = await self.repository.mark_completed(
                public_id=record.public_id,
                extraction=extraction_metadata,
                parser=parser_metadata,
                normalized_text=normalized_text,
                normalized_content=parsed_content
            )
            if completed_document is None:
                raise ProcessingError('CV record disappeared during processing')
            return self.repository.deserialize(completed_document)
        except Exception as exc:
            error_message = str(exc)
            await self.repository.mark_failed(record.public_id, error_message)
            if isinstance(exc, ProcessingError):
                raise
            raise ProcessingError('Unable to parse uploaded CV') from exc


@lru_cache
def get_cv_ingestion_service() -> CVIngestionService:
    return CVIngestionService()
