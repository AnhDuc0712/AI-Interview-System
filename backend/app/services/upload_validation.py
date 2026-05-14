import logging
import re
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.models.cv import CVFileType

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES: dict[CVFileType, set[str]] = {
    CVFileType.pdf: {'application/pdf', 'application/octet-stream', ''},
    CVFileType.docx: {
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/octet-stream',
        ''
    },
}

PDF_SIGNATURE_PATTERN = re.compile(br'%PDF-\d\.\d')
DOCX_SIGNATURES: tuple[bytes, ...] = (b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08')
SIGNATURE_SCAN_LIMIT = 1024
LOG_PRINT_LIMIT = 32


def _format_signature_snippet(content: bytes) -> str:
    return repr(content[:LOG_PRINT_LIMIT])


def _detect_file_signature(content: bytes) -> str:
    head = content[:SIGNATURE_SCAN_LIMIT]
    if PDF_SIGNATURE_PATTERN.search(head):
        return 'pdf'
    if any(signature in head for signature in DOCX_SIGNATURES):
        return 'zip'
    return 'unknown'


def _is_valid_pdf(content: bytes) -> bool:
    return bool(PDF_SIGNATURE_PATTERN.search(content[:SIGNATURE_SCAN_LIMIT]))


def _is_valid_docx(content: bytes) -> bool:
    head = content[:SIGNATURE_SCAN_LIMIT]
    return any(signature in head for signature in DOCX_SIGNATURES)


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
        if not content:
            raise ValidationError('Uploaded file is empty')

        file_signature = _detect_file_signature(content)
        logger.debug(
            'Validating CV upload signature: first_bytes=%s detected_signature=%s expected_type=%s',
            _format_signature_snippet(content),
            file_signature,
            file_type.value,
        )

        if file_type == CVFileType.pdf:
            if not _is_valid_pdf(content):
                raise ValidationError('Uploaded file content is not a valid PDF')
        elif file_type == CVFileType.docx:
            if not _is_valid_docx(content):
                raise ValidationError('Uploaded file content is not a valid DOCX')
