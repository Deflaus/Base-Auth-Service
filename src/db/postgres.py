import uuid


def get_postgres() -> dict:
    return {
        "johndoe": {
            "pk": uuid.UUID("79825d54-0ca7-4324-9543-453729496b95"),
            "username": "johndoe",
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "hashed_password": "$2b$12$CeUrZPurx9jv7Ni844dT0uCgVGoV3N75El6K8qaBk1pZCnYfaZ7j2",
            "is_active": False,
        }
    }
