import uuid


def get_postgres() -> dict:
    return {
        "79825d54-0ca7-4324-9543-453729496b95": {
            "pk": uuid.UUID("79825d54-0ca7-4324-9543-453729496b95"),
            "username": "first_user",
            "full_name": "First User",
            "email": "first_user@example.com",
            "hashed_password": "$2b$12$CeUrZPurx9jv7Ni844dT0uCgVGoV3N75El6K8qaBk1pZCnYfaZ7j2",
            "is_active": False,
        }
    }
