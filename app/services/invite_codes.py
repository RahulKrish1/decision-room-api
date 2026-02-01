import secrets

def new_invite_code(length: int = 10) -> str:
    # URL-safe and readable-ish
    return secrets.token_urlsafe(16)[:length]
