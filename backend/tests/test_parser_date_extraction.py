import re

import pytest

from app.ai.parser import extractor


def test_extract_year_supports_named_groups(monkeypatch) -> None:
    monkeypatch.setattr(extractor, 'DATE_YEAR_PATTERN', re.compile(r'(?P<year>20\d{2})'))
    assert extractor._extract_year('Started in 2024') == '2024'


def test_extract_year_supports_unnamed_groups(monkeypatch) -> None:
    monkeypatch.setattr(extractor, 'DATE_YEAR_PATTERN', re.compile(r'(20\d{2})'))
    assert extractor._extract_year('Started in 2024') == '2024'


@pytest.mark.parametrize(
    'line,expected_start,expected_end',
    [
        ('2024 - 2025', '2024', '2025'),
        ('02/2025 - 05/2025', '02/2025', '05/2025'),
        ('Sep 2025 - Dec 2025', 'Sep 2025', 'Dec 2025'),
        ('2024-Present', '2024', 'Present'),
        ('Present', None, 'Present'),
        ('Current', None, 'Current'),
        ('Expected', None, 'Expected'),
        ('2024 -', '2024', None),
        ('Malformed date 20X4', None, None),
    ],
)
def test_parse_date_range_handles_real_world_formats(line: str, expected_start: str | None, expected_end: str | None) -> None:
    start, end = extractor._parse_date_range(line)
    assert start == expected_start
    assert end == expected_end


def test_parse_date_range_does_not_crash_on_malformed_text() -> None:
    start, end = extractor._parse_date_range('Senior Backend Engineer — AI Interview System')
    assert start is None
    assert end is None
