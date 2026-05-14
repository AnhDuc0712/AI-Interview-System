from __future__ import annotations

from datetime import datetime, timezone

from app.models.cv import CVParserMetadata, StructuredCVData
from app.ai.parser.cleaner import clean_text
from app.ai.parser.extractor import (
    extract_certifications,
    extract_education,
    extract_experience,
    extract_personal_info,
    extract_projects,
)
from app.ai.parser.section_detector import split_sections
from app.ai.skills.extractor import SkillExtractionEngine


# Parser pipeline architecture:
# 1. Clean extracted text
# 2. Detect sections
# 3. Parse personal info and structured sections
# 4. Route skills through the new SkillExtractionEngine


class RuleBasedCVParserService:
    parser_name = 'rule-based-structured-cv-parser'
    parser_version = 'v1'

    def parse(self, normalized_text: str) -> tuple[StructuredCVData, CVParserMetadata]:
        cleaned_text = clean_text(normalized_text)
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        sections = split_sections(lines)
        personal_info = extract_personal_info(lines, sections.get('summary', []))
        skill_extraction = SkillExtractionEngine().extract(cleaned_text, section_lines=sections.get('skills', []))

        parsed = StructuredCVData(
            personal_info=personal_info,
            skills=skill_extraction.skills,
            categorized_skills=skill_extraction.categorized_skills,
            experience=extract_experience(sections.get('experience', [])),
            education=extract_education(sections.get('education', [])),
            projects=extract_projects(sections.get('projects', [])),
            certifications=extract_certifications(sections.get('certifications', [])),
            raw_sections=sections,
        )

        metadata = CVParserMetadata(
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            parsed_at=datetime.now(timezone.utc),
        )
        return parsed, metadata


# Example parsed output structure:
# {
#   'personal_info': {
#       'full_name': 'Ada Lovelace',
#       'email': 'ada@example.com',
#       'phone': '+1 555 111 2222',
#       'linkedin': 'https://linkedin.com/in/ada-lovelace',
#       'github': 'https://github.com/adalovelace',
#       'location': 'London, UK',
#       'summary': 'Backend engineer focused on AI systems.',
#   },
#   'skills': ['Python', 'FastAPI', 'MongoDB'],
#   'experience': [ ... ],
#   'education': [ ... ],
#   'projects': [ ... ],
#   'certifications': [ ... ],
#   'raw_sections': { ... },
# }
