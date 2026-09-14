"""Authentication and password/security-question helpers."""
from __future__ import annotations

import hashlib
import re
import secrets
import string
from typing import Iterable

COMMON_PASSWORDS = {
    "password", "password1", "password123", "123456789", "qwerty123",
    "abcdefgh", "abcdefgh1", "letmein123", "welcome123", "admin123",
}


def secure_hash(value: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", value.encode("utf-8"), salt, 310_000)
    return digest.hex(), salt.hex()


def verify_hash(value: str, digest_hex: str, salt_hex: str) -> bool:
    digest, _ = secure_hash(value, bytes.fromhex(salt_hex))
    return secrets.compare_digest(digest, digest_hex)


def password_checks(password: str) -> dict[str, bool]:
    lower = password.lower()
    repeated = bool(re.search(r"(.)\1\1", password))
    sequence = any(seq in lower for seq in ("012345", "123456", "234567", "345678", "456789", "abcdef", "qwerty"))
    return {
        "Minimum 9 characters": len(password) >= 9,
        "Uppercase letter": bool(re.search(r"[A-Z]", password)),
        "Lowercase letter": bool(re.search(r"[a-z]", password)),
        "Number": bool(re.search(r"\d", password)),
        "Special character": bool(re.search(r"[^A-Za-z0-9]", password)),
        "Not a common password": lower not in COMMON_PASSWORDS,
        "Not a repeated / obvious pattern": not repeated and not sequence,
    }


def validate_password(password: str) -> tuple[bool, list[str]]:
    checks = password_checks(password)
    failed = [label for label, ok in checks.items() if not ok]
    return not failed, failed


def generate_secure_password(length: int = 12) -> str:
    if length < 9:
        length = 9
    pools = [string.ascii_uppercase, string.ascii_lowercase, string.digits, "!@#$%^&*_-+=?"]
    chars = [secrets.choice(pool) for pool in pools]
    all_chars = "".join(pools)
    chars.extend(secrets.choice(all_chars) for _ in range(length - len(chars)))
    secrets.SystemRandom().shuffle(chars)
    password = "".join(chars)
    ok, _ = validate_password(password)
    return password if ok else generate_secure_password(length + 1)
