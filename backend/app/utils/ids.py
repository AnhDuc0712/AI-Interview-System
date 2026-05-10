import secrets


def generate_public_id(prefix: str = 'usr') -> str:
    return f'{prefix}_{secrets.token_urlsafe(9).rstrip("=")}'
