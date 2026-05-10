from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.models.cv import CVFileType


ALLOWED_CONTENT_TYPES: dict[CVFileType, set[str]] = {
    CVFileType.pdf: {'application/pdf', 'application/octet-stream', ''},
    CVFileType.docx: {
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/octet-stream',
        ''
    },
}


class UploadValidationService:
    def validate_filename(self, filename: str | None) -> tuple[str, CVFileType]:
        if not filename:
            raise ValidationError('Uploaded file must include a filename')

        cleaned_name = Path(filename).name
        extension = Path(cleaned_name).suffix.lower()
        if extension == '.pdf':
            return cleaned_name, CVFileType.pdf
        if extension == '.docx':
            return cleaned_name, CVFileType.docx
        raise ValidationError('Only PDF and DOCX CV uploads are supported')

    def validate_content_type(self, upload_file: UploadFile, file_type: CVFileType) -> str:
        content_type = upload_file.content_type or ''
        if content_type not in ALLOWED_CONTENT_TYPES[file_type]:
            raise ValidationError(f'Invalid content type for {file_type.value} upload')
        return content_type

    def validate_size(self, size_bytes: int) -> None:
        if size_bytes <= 0:
            raise ValidationError('Uploaded file is empty')
        if size_bytes > settings.cv_max_file_size_bytes:
            raise ValidationError('Uploaded file exceeds the maximum allowed size')

    def validate_signature(self, content: bytes, file_type: CVFileType) -> None:
        if file_type == CVFileType.pdf and not content.startswith(b'%PDF'):
            raise ValidationError('Uploaded file content is not a valid PDF')
        if file_type == CVFileType.docx and not content.startswith(b'PK'):
            raise ValidationError('Uploaded file content is not a valid DOCX')
