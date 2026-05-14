import pytest

from app.core.exceptions import ValidationError
from app.models.cv import CVFileType
from app.services.upload_validation import UploadValidationService


def test_validate_signature_accepts_standard_pdf() -> None:
    service = UploadValidationService()
    service.validate_signature(b'%PDF-1.7\n1 0 obj\n', CVFileType.pdf)


def test_validate_signature_accepts_pdf_with_bom() -> None:
    service = UploadValidationService()
    service.validate_signature(b'\xef\xbb\xbf%PDF-1.5\n1 0 obj\n', CVFileType.pdf)


def test_validate_signature_accepts_pdf_with_leading_whitespace() -> None:
    service = UploadValidationService()
    service.validate_signature(b'   \n\t%PDF-1.6\n1 0 obj\n', CVFileType.pdf)


def test_validate_signature_accepts_topcv_like_pdf() -> None:
    service = UploadValidationService()
    service.validate_signature(
        b'\xef\xbb\xbf  %PDF-1.6\n%\xc3\xa2\xc3\xa3\xc3\x8f\xc3\x93\n',
        CVFileType.pdf,
    )


def test_validate_signature_rejects_corrupted_pdf() -> None:
    service = UploadValidationService()
    with pytest.raises(ValidationError, match='valid PDF'):
        service.validate_signature(b'%PDA-1.4\nnot a pdf', CVFileType.pdf)


def test_validate_signature_rejects_renamed_txt_file() -> None:
    service = UploadValidationService()
    with pytest.raises(ValidationError, match='valid PDF'):
        service.validate_signature(b'This is a plain text file masquerading as PDF', CVFileType.pdf)
