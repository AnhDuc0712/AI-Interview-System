import json
import os
import re
from typing import Any

import httpx

from app.core.config import settings


_SECTION_HEADERS = {
    'career objective',
    'objective',
    'summary',
    'profile',
    'work experience',
    'experience',
    'projects',
    'education',
    'skills',
    'certifications',
    'awards',
    'languages',
    'activities',
}

_ROLE_MARKERS = (
    '.NET',
    'Backend',
    'Frontend',
    'Fullstack',
    'Full-Stack',
    'Software',
    'Developer',
    'Engineer',
    'Intern',
    'QA',
    'DevOps',
    'Data',
    'Mobile',
)


def _normalize_line(value: str) -> str:
    value = value.replace('\u2022', '-').replace('\u2023', '-').replace('\u25e6', '-').replace('\uf0b7', '-')
    return re.sub(r'\s+', ' ', value.replace('\r', ' ')).strip()


def _is_bullet_line(line: str) -> bool:
    return bool(re.match(r'^[-*]\s+', line))


def _is_section_header(line: str) -> bool:
    normalized = line.strip().lower().rstrip(':')
    return normalized in _SECTION_HEADERS


def _looks_like_date(line: str) -> bool:
    return bool(
        re.search(r'\b\d{1,2}/\d{4}\s*-\s*(?:\d{1,2}/\d{4}|present|current)\b', line, flags=re.IGNORECASE)
        or re.search(r'\b\d{4}\s*-\s*(?:\d{4}|present|current)\b', line, flags=re.IGNORECASE)
    )


def _should_merge_lines(previous: str, current: str) -> bool:
    if not previous or not current:
        return False
    if _is_bullet_line(previous) or _is_bullet_line(current):
        return False
    if _is_section_header(current) or _looks_like_date(current):
        return False
    if previous.endswith((':', ';')):
        return False
    if re.search(r'[.!?]$', previous):
        return False
    if current.isupper():
        return False
    if re.match(r'^(position|tech|technologies|gpa)\s*:', current, flags=re.IGNORECASE):
        return False
    return True


def _preprocess_cv_text(text: str) -> str:
    lines = [_normalize_line(line) for line in text.splitlines()]
    merged_lines: list[str] = []
    current = ''

    for line in lines:
        if not line:
            if current:
                merged_lines.append(current)
                current = ''
            continue

        if _is_bullet_line(line):
            if current:
                merged_lines.append(current)
                current = ''
            merged_lines.append(line)
            continue

        if not current:
            current = line
            continue

        if _should_merge_lines(current, line):
            current = f'{current} {line}'
        else:
            merged_lines.append(current)
            current = line

    if current:
        merged_lines.append(current)

    return '\n'.join(merged_lines)


def _strip_code_fences(raw_text: str) -> str:
    fenced = raw_text.strip()
    if fenced.startswith('```'):
        fenced = re.sub(r'^```(?:json)?\s*', '', fenced)
        fenced = re.sub(r'\s*```$', '', fenced)
    return fenced.strip()


def _safe_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return _normalize_line(value) or None
    return _normalize_line(str(value)) or None


def _safe_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [value]
    return [value]


def _normalize_date(value: Any) -> str | None:
    text = _safe_string(value)
    if not text:
        return None
    return text.replace('Present', 'present').replace('Current', 'current')


def _extract_name_from_first_line(text: str) -> str | None:
    role_pattern = '|'.join(re.escape(marker) for marker in _ROLE_MARKERS)
    for raw_line in text.splitlines():
        line = _normalize_line(raw_line)
        if not line or '@' in line or re.search(r'\d{8,}', line):
            continue
        line = re.sub(rf'(?=({role_pattern}))', ' ', line)
        candidate = re.split(r'\s{2,}|[|]', line, maxsplit=1)[0].strip(' -,:')
        role_split = re.split(
            r'(?=\s*(?:\.NET|Backend|Frontend|Fullstack|Full-Stack|Software|Developer|Engineer|Intern|QA|DevOps|Data|Mobile)\b)',
            candidate,
            maxsplit=1,
        )
        candidate = role_split[0].strip(' -,:.')
        if len(candidate.split()) >= 2:
            return candidate
    return None


def _extract_name_from_email(email: str | None) -> str | None:
    if not email or '@' not in email:
        return None
    prefix = email.split('@', 1)[0]
    cleaned = re.sub(r'\d+', ' ', prefix)
    tokens = [token for token in re.split(r'[._-]+|\s+', cleaned) if token]
    if len(tokens) < 2:
        return None
    return ' '.join(token.capitalize() for token in tokens)


def _merge_sentence_fragments(lines: list[str]) -> list[str]:
    merged: list[str] = []
    buffer = ''

    for line in lines:
        cleaned = _safe_string(line)
        if not cleaned:
            continue
        cleaned = re.sub(r'^[-*]\s*', '', cleaned).strip()
        if not cleaned:
            continue
        if not buffer:
            buffer = cleaned
            continue
        if re.search(r'[.!?]$', buffer):
            merged.append(buffer)
            buffer = cleaned
            continue
        if cleaned[:1].islower() or len(cleaned.split()) <= 4:
            buffer = f'{buffer} {cleaned}'
        else:
            merged.append(buffer)
            buffer = cleaned

    if buffer:
        merged.append(buffer)

    return merged


def _normalize_responsibilities(value: Any) -> list[str]:
    raw_items: list[str] = []
    for item in _safe_list(value):
        if item is None:
            continue
        if isinstance(item, dict):
            text = _safe_string(item.get('text') or item.get('description') or item.get('value'))
            if text:
                raw_items.append(text)
            continue
        text = _safe_string(item)
        if not text:
            continue
        split_items = [
            segment.strip()
            for segment in re.split(r'(?:\n+|(?<=\s)-\s+|(?<=\s)\*\s+)', text)
            if segment and segment.strip()
        ]
        raw_items.extend(split_items or [text])

    return _merge_sentence_fragments(raw_items)


def _normalize_technologies(value: Any) -> list[str]:
    technologies: list[str] = []
    for item in _safe_list(value):
        if isinstance(item, str):
            technologies.extend(part.strip() for part in re.split(r'[,/|]', item) if part.strip())
            continue
        text = _safe_string(item)
        if text:
            technologies.append(text)
    return list(dict.fromkeys(technologies))


def _extract_gpa(text: str) -> str | None:
    match = re.search(r'\b\d(?:\.\d{1,2})?\s*/\s*4(?:\.0)?\b', text)
    if not match:
        return None
    return match.group(0).replace(' ', '')


def _extract_date_range(text: str) -> tuple[str | None, str | None]:
    match = re.search(
        r'\b(\d{1,2}/\d{4}|\d{4})\s*-\s*(\d{1,2}/\d{4}|\d{4}|present|current)\b',
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None, None
    return match.group(1), match.group(2)


def _normalize_personal_info(data: dict[str, Any], source_text: str) -> dict[str, Any]:
    personal_info = data.get('personal_info')
    if not isinstance(personal_info, dict):
        personal_info = {}

    email = _safe_string(personal_info.get('email'))
    resolved_name = (
        _safe_string(personal_info.get('name'))
        or _safe_string(personal_info.get('full_name'))
        or _extract_name_from_first_line(source_text)
        or _extract_name_from_email(email)
    )

    return {
        'name': resolved_name,
        'full_name': resolved_name,
        'email': email,
        'phone': _safe_string(personal_info.get('phone')),
        'github': _safe_string(personal_info.get('github')),
        'linkedin': _safe_string(personal_info.get('linkedin')),
        'location': _safe_string(personal_info.get('location')),
        'summary': _safe_string(personal_info.get('summary')),
    }


def _normalize_experience(items: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in _safe_list(items):
        if not isinstance(item, dict):
            continue
        responsibilities = _normalize_responsibilities(
            item.get('responsibilities') or item.get('description') or item.get('highlights')
        )
        normalized.append(
            {
                'company': _safe_string(item.get('company')),
                'title': _safe_string(item.get('title') or item.get('role') or item.get('position')),
                'start_date': _normalize_date(item.get('start_date')),
                'end_date': _normalize_date(item.get('end_date')),
                'location': _safe_string(item.get('location')),
                'responsibilities': responsibilities,
                'description': ' '.join(responsibilities) if responsibilities else None,
            }
        )
    return normalized


def _normalize_education(items: Any, source_text: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    fallback_gpa = _extract_gpa(source_text)

    for item in _safe_list(items):
        if not isinstance(item, dict):
            continue
        item_text = ' '.join(
            filter(
                None,
                [
                    _safe_string(item.get('institution') or item.get('school') or item.get('university')),
                    _safe_string(item.get('degree')),
                    _safe_string(item.get('field')) or _safe_string(item.get('field_of_study')),
                    _safe_string(item.get('gpa')),
                    _safe_string(item.get('date_range')),
                ],
            )
        )

        start_date = _normalize_date(item.get('start_date'))
        end_date = _normalize_date(item.get('end_date') or item.get('graduation_date'))
        if not start_date or not end_date:
            inferred_start, inferred_end = _extract_date_range(item_text)
            start_date = start_date or inferred_start
            end_date = end_date or inferred_end

        gpa = _safe_string(item.get('gpa')) or _extract_gpa(item_text) or fallback_gpa
        normalized.append(
            {
                'institution': _safe_string(item.get('institution') or item.get('school') or item.get('university')),
                'degree': _safe_string(item.get('degree')),
                'field_of_study': _safe_string(item.get('field_of_study') or item.get('field') or item.get('major')),
                'start_date': start_date,
                'end_date': end_date,
                'graduation_date': end_date,
                'gpa': gpa,
            }
        )
    return normalized


def _normalize_projects(items: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in _safe_list(items):
        if not isinstance(item, dict):
            continue
        description_parts = _normalize_responsibilities(
            item.get('responsibilities') or item.get('description') or item.get('highlights')
        )
        if not description_parts:
            summary = _safe_string(item.get('summary'))
            if summary:
                description_parts = [summary]
        normalized.append(
            {
                'name': _safe_string(item.get('name') or item.get('title')),
                'description': ' '.join(description_parts) if description_parts else None,
                'technologies': _normalize_technologies(item.get('technologies') or item.get('tech_stack') or item.get('tech')),
                'start_date': _normalize_date(item.get('start_date')),
                'end_date': _normalize_date(item.get('end_date')),
            }
        )
    return normalized


def _normalize_certifications(items: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in _safe_list(items):
        if isinstance(item, dict):
            normalized.append(
                {
                    'name': _safe_string(item.get('name') or item.get('title')),
                    'issuer': _safe_string(item.get('issuer') or item.get('organization')),
                    'date': _normalize_date(item.get('date') or item.get('issued_at')),
                }
            )
            continue
        name = _safe_string(item)
        if name:
            normalized.append({'name': name, 'issuer': None, 'date': None})
    return normalized


def _normalize_string_list(items: Any) -> list[str]:
    values: list[str] = []
    for item in _safe_list(items):
        text = _safe_string(item)
        if not text:
            continue
        values.extend(part.strip() for part in re.split(r'[,|/]', text) if part.strip())
    return list(dict.fromkeys(values))


def _normalize_payload(data: dict[str, Any], source_text: str) -> dict[str, Any]:
    categorized_skills = data.get('categorized_skills')
    raw_sections = data.get('raw_sections')
    return {
        'personal_info': _normalize_personal_info(data, source_text),
        'skills': _normalize_string_list(data.get('skills')),
        'education': _normalize_education(data.get('education'), source_text),
        'experience': _normalize_experience(data.get('experience')),
        'projects': _normalize_projects(data.get('projects')),
        'certifications': _normalize_certifications(data.get('certifications')),
        'languages': _normalize_string_list(data.get('languages')),
        'categorized_skills': categorized_skills if isinstance(categorized_skills, dict) else {},
        'raw_sections': raw_sections if isinstance(raw_sections, dict) else {},
    }


async def parse(text: str) -> dict[str, Any]:
    api_key = settings.gemini_api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {}

    model = 'models/gemini-2.5-flash'
    url = f'https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={api_key}'
    preprocessed_text = _preprocess_cv_text(text)

    prompt = f"""Extract structured information from this CV and return ONLY valid JSON.

The CV text may contain broken line breaks from PDF extraction, wrapped sentences, and inconsistent bullet markers such as "-", "*", and bullet dots.
You must reconstruct coherent entries by merging wrapped lines that belong to the same sentence or bullet.

Rules:
1. Put the candidate's full name in both personal_info.name and personal_info.full_name.
2. Preserve GPA exactly when written like "3.09/4.0".
3. For experience.responsibilities, always return an array of complete bullet points. Never return null.
4. For project descriptions, merge fragmented lines into a complete description.
5. If dates are partial, keep the original detected format instead of inventing missing months.
6. Return empty arrays for missing list sections.
7. Prefer null for missing scalar values.

CV TEXT:
{preprocessed_text[:30000]}

Required JSON structure:
{{
  "personal_info": {{
    "name": "string",
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "github": "string",
    "linkedin": "string",
    "summary": "string"
  }},
  "skills": ["skill1", "skill2"],
  "education": [
    {{
      "institution": "string",
      "degree": "string",
      "field_of_study": "string",
      "start_date": "YYYY-MM or YYYY",
      "end_date": "YYYY-MM or YYYY",
      "gpa": "3.09/4.0"
    }}
  ],
  "experience": [
    {{
      "company": "string",
      "title": "string",
      "start_date": "YYYY-MM or YYYY",
      "end_date": "YYYY-MM or YYYY or present",
      "location": "string",
      "responsibilities": ["complete sentence", "complete sentence"]
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "technologies": ["string"],
      "start_date": "YYYY-MM or YYYY",
      "end_date": "YYYY-MM or YYYY"
    }}
  ],
  "certifications": [
    {{
      "name": "string",
      "issuer": "string",
      "date": "YYYY-MM or YYYY"
    }}
  ],
  "languages": ["string"]
}}
"""

    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'temperature': 0.1,
            'responseMimeType': 'application/json',
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                print(f'Gemini error body: {response.text}')
                return {}

            result = response.json()
            text_response = (
                result.get('candidates', [{}])[0]
                .get('content', {})
                .get('parts', [{}])[0]
                .get('text', '{}')
            )
            parsed = json.loads(_strip_code_fences(text_response))
            if not isinstance(parsed, dict):
                return {}
            return _normalize_payload(parsed, preprocessed_text)
        except Exception as exc:
            print(f'Gemini exception: {exc}')
            return {}
