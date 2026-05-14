import re


def clean_text(text: str) -> str:
    """Normalize document whitespace and preserve section boundaries."""
    cleaned = text.replace('\r\n', '\n').replace('\r', '\n')
    cleaned = cleaned.replace('\t', ' ')
    cleaned = re.sub(r'[ \u00A0]{2,}', ' ', cleaned)
    cleaned = re.sub(r'[\u2022\*•]+', '-', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r'^[ \t\-]*\n', '\n', cleaned, flags=re.MULTILINE)
    return cleaned.strip()
