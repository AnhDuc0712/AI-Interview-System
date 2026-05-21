import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

from app.core.config import settings
from app.services import gemini_cv_parser
from app.models.cv import CVParserMetadata


class HybridCVParserService:
    parser_name = "hybrid-cv-parser"
    parser_version = "v1"

    async def parse(self, normalized_text: str) -> Tuple[Dict[str, Any], CVParserMetadata]:
        """
        Parse CV using Gemini.
        Returns (parsed_content, parser_metadata_object)
        """
        print(f"Calling Gemini parser for CV...")

        parsed_content = await gemini_cv_parser.parse(normalized_text)

        parser_metadata = CVParserMetadata(
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            parsed_at=datetime.now(timezone.utc),
        )

        print(f"Gemini parsing completed. Skills: {len(parsed_content.get('skills', []))}")

        return parsed_content, parser_metadata


def get_hybrid_parser() -> HybridCVParserService:
    return HybridCVParserService()
