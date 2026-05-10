from typing import Any


def extract_bearer_token(authorization_header: str | None) -> str | None:
    if not authorization_header:
        return None

    scheme, _, token = authorization_header.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return None
    return token.strip()


def extract_email_from_claims(payload: dict[str, Any]) -> str | None:
    email_candidates = (
        payload.get('email'),
        payload.get('email_address'),
        payload.get('primary_email_address')
    )
    for value in email_candidates:
        if isinstance(value, str) and value:
            return value
    return None


def extract_full_name(payload: dict[str, Any]) -> str | None:
    full_name = payload.get('name') or payload.get('full_name')
    if isinstance(full_name, str) and full_name:
        return full_name

    first_name = payload.get('first_name')
    last_name = payload.get('last_name')
    parts = [part for part in (first_name, last_name) if isinstance(part, str) and part]
    return ' '.join(parts) if parts else None
