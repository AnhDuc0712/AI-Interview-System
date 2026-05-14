from app.services.cv_parser import StructuredCVParserService
from app.services.text_normalizer import TextNormalizationService


def test_text_normalizer_collapses_spacing():
    service = TextNormalizationService()

    normalized = service.normalize('Ada   Lovelace\r\n\r\n\r\nPython\t\tFastAPI')

    assert normalized == 'Ada Lovelace\n\nPython FastAPI'


def test_structured_cv_parser_extracts_core_sections():
    parser = StructuredCVParserService()
    text = """Ada Lovelace
ada@example.com
+1 555 111 2222
London, UK
github.com/adalovelace
linkedin.com/in/ada-lovelace

Summary
Backend engineer focused on AI systems.

Skills
ReactJS, react.js, FastAPI, nodejs, Node.js, MongoDB, mongodb, docker, Docker

Experience
Senior Backend Engineer - AI Interview System

Projects
Interview Copilot - AI-guided mock interview workspace

Education
University of London - BSc - Computer Science
"""

    parsed, metadata = parser.parse(text)

    assert parsed.personal_info.full_name == 'Ada Lovelace'
    assert parsed.personal_info.email == 'ada@example.com'
    assert parsed.personal_info.github == 'https://github.com/adalovelace'
    assert parsed.personal_info.linkedin == 'https://linkedin.com/in/ada-lovelace'
    assert parsed.personal_info.location == 'London, UK'
    assert parsed.skills == ['React', 'FastAPI', 'Node.js', 'MongoDB', 'Docker']
    assert parsed.categorized_skills['frontend'] == ['React']
    assert parsed.categorized_skills['backend'] == ['FastAPI', 'Node.js']
    assert parsed.categorized_skills['database'] == ['MongoDB']
    assert parsed.categorized_skills['devops'] == ['Docker']
    assert parsed.experience[0].title == 'Senior Backend Engineer'
    assert parsed.projects[0].name == 'Interview Copilot'
    assert parsed.education[0].institution == 'University of London'
    assert metadata.parser_version == 'v1'
