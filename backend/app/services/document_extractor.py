import asyncio
import io

from app.core.exceptions import ProcessingError
from app.models.cv import CVFileType


class PDFTextExtractor:
    name = 'pypdf'
    version = '1.0'

    async def extract(self, content: bytes) -> str:
        return await asyncio.to_thread(self._extract_sync, content)

    def _extract_sync(self, content: bytes) -> str:
        try:
            from pypdf import PdfReader
            # Clean BOM and leading garbage bytes that can cause 'invalid pdf header' errors
            raw_data = content
            if raw_data.startswith(b'\xef\xbb\bf'):
                raw_data = raw_data[3:]
            pdf_pos = raw_data.find(b'%PDF')
            if pdf_pos > 0:
                raw_data = raw_data[pdf_pos:]

            reader = PdfReader(io.BytesIO(raw_data))
            pages = [page.extract_text() or '' for page in reader.pages]
            return '\n'.join(pages)
        except Exception as exc:
            raise ProcessingError('Unable to extract text from PDF file') from exc


class DOCXTextExtractor:
    name = 'python-docx'
    version = '1.0'

    async def extract(self, content: bytes) -> str:
        return await asyncio.to_thread(self._extract_sync, content)

    def _extract_sync(self, content: bytes) -> str:
        try:
            from docx import Document

            document = Document(io.BytesIO(content))
            paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
            return '\n'.join(paragraphs)
        except Exception as exc:
            raise ProcessingError('Unable to extract text from DOCX file') from exc


class DocumentExtractionService:
    def __init__(self) -> None:
        self.pdf_extractor = PDFTextExtractor()
        self.docx_extractor = DOCXTextExtractor()

    async def extract_text(self, file_type: CVFileType, content: bytes) -> tuple[str, str, str]:
        if file_type == CVFileType.pdf:
            text = await self.pdf_extractor.extract(content)
            return text, self.pdf_extractor.name, self.pdf_extractor.version
        if file_type == CVFileType.docx:
            text = await self.docx_extractor.extract(content)
            return text, self.docx_extractor.name, self.docx_extractor.version
        raise ProcessingError('Unsupported document type for extraction')
