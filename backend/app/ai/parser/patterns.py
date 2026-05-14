from __future__ import annotations

import re

SECTION_HEADERS: dict[str, set[str]] = {
    'experience': {
        'experience',
        'work experience',
        'professional experience',
        'employment history',
        'career history',
    },
    'education': {
        'education',
        'academic background',
        'education and training',
        'academic qualifications',
    },
    'skills': {
        'skills',
        'technical skills',
        'core skills',
        'skills summary',
        'expertise',
    },
    'projects': {
        'projects',
        'personal projects',
        'selected projects',
        'project highlights',
    },
    'certifications': {
        'certifications',
        'licenses',
        'certificates',
        'certification',
    },
    'summary': {
        'summary',
        'professional summary',
        'profile',
        'career summary',
        'about me',
    },
}

EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.[a-z]{2,}', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'(?:(?:\+?\d{1,3}[\s\-\(\)]*)?\d[\d\s\-\(\)]{7,}\d)')
GITHUB_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?github\.com/(?P<username>[A-Za-z0-9_.-]+)', re.IGNORECASE)
LINKEDIN_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|pub)/(?P<identifier>[A-Za-z0-9_-]+)', re.IGNORECASE)
URL_PATTERN = re.compile(r'https?://[^\s,;]+' , re.IGNORECASE)
DATE_RANGE_PATTERN = re.compile(
    r'(?P<start>(?:\d{4}|[A-Za-z]{3,9}\s+\d{4}|\d{1,2}/\d{4}))\s*(?:-|–|—)\s*'
    r'(?P<end>(?:Present|Current|Expected|Now|Ongoing|[A-Za-z]{3,9}\s+\d{4}|\d{1,2}/\d{4}|\d{4}))',
    re.IGNORECASE
)
DATE_WORD_PATTERN = re.compile(r'\b(Present|Current|Expected|Now|Ongoing)\b', re.IGNORECASE)
DATE_YEAR_PATTERN = re.compile(r'\b(20\d{2}|19\d{2})\b')
BULLET_SPLIT_PATTERN = re.compile(r'[\u2022\*•;]+')
SECTION_SPLIT_PATTERN = re.compile(r'\s+[-–—@|:]\s+')

NOISE_NAME_LINES = {
    'resume',
    'curriculum vitae',
    'cv',
    'professional profile',
}
