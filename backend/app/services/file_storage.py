import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from app.core.config import PROJECT_ROOT, settings
from app.models.cv import CVStorageProvider, StoredFileMetadata


@dataclass
class StoredFileResult:
    metadata: StoredFileMetadata


class LocalFileStorageService:
    def __init__(self, base_path: str | None = None) -> None:
        configured_path = Path(base_path or settings.cv_upload_dir)
        if configured_path.is_absolute():
            self.base_path = configured_path
        else:
            self.base_path = PROJECT_ROOT / configured_path

    async def ensure_ready(self) -> None:
        await asyncio.to_thread(self.base_path.mkdir, parents=True, exist_ok=True)

    async def save(
        self,
        *,
        owner_public_id: str,
        cv_public_id: str,
        filename: str,
        content_type: str,
        content: bytes
    ) -> StoredFileResult:
        now = datetime.now(timezone.utc)
        relative_path = Path(owner_public_id) / cv_public_id / filename
        absolute_path = self.base_path / relative_path
        await asyncio.to_thread(absolute_path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(absolute_path.write_bytes, content)

        metadata = StoredFileMetadata(
            provider=CVStorageProvider.local,
            path=str(relative_path).replace('\\', '/'),
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            checksum_sha256=sha256(content).hexdigest(),
            uploaded_at=now
        )
        return StoredFileResult(metadata=metadata)
