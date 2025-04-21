import os
from typing import List, Optional, Union, Annotated

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, BeforeValidator
from pydantic_settings import BaseSettings


def assemble_cors_origins(v: Union[str, List[str]]) -> Union[List[str], str]:
    """
    Assembles CORS origins from either a comma-separated string or a list.

    Args:
        v: Either a comma-separated string of origins or a list of origins

    Returns:
        List of origins or the original input if already in correct format

    Raises:
        ValueError: If the input format is invalid
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CodeSnippets API"

    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    # e.g: "http://localhost:3000,http://localhost:8000"
    BACKEND_CORS_ORIGINS: Annotated[List[AnyHttpUrl], BeforeValidator(assemble_cors_origins)] = []

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: PostgresDsn

    # Server
    PORT: int = 8000

    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


settings = Settings()
