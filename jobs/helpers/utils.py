from dotenv import dotenv_values
import uuid


def get_env(key: str) -> str:
    env_vars = dotenv_values(".env")
    return env_vars[key]


def json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
