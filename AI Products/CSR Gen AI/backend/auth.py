"""Authentication utilities: password hashing, cookie session management."""

import hashlib
import hmac
import json
import secrets
import time

from .config import SECRET_KEY, COOKIE_NAME, COOKIE_MAX_AGE


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, expected = hashed.split("$", 1)
    except ValueError:
        return False
    computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return hmac.compare_digest(computed.hex(), expected)


def create_session_token(user_id: int) -> str:
    """Create a signed session token."""
    payload = json.dumps({"uid": user_id, "exp": int(time.time()) + COOKIE_MAX_AGE})
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}|{sig}"


def decode_session_token(token: str) -> int | None:
    """Verify and decode session token, return user_id or None."""
    try:
        payload_str, sig = token.rsplit("|", 1)
        expected = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(payload_str)
        if payload.get("exp", 0) < time.time():
            return None
        return payload["uid"]
    except Exception:
        return None
