import re


def check_name(value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()

def check_phone(value):
    if not re.fullmatch(r"[6-9]\d{9}", value):
        raise ValueError("Enter a valid 10-digit Indian phone number")
    return value


def validate_email(value: str) -> str:
    value = value.strip()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.fullmatch(pattern, value):
        raise ValueError("Enter a valid email address")

    return value.lower()


def validate_password(value: str) -> str:
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password needs an uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password needs a lowercase letter")
    if not re.search(r"\d", value):
        raise ValueError("Password needs a digit")
    if not re.search(r"[^A-Za-z0-9]", value):
        raise ValueError("Password needs a special character")
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password must not exceed 72 UTF-8 bytes")

    return value