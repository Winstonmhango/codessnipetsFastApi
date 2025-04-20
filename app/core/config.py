import os
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CodeSnippets API"

    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    # e.g: "http://localhost:3000,http://localhost:8000"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(self, v: Union[str, List[str]]) -> Union[List[str], str]:
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

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: PostgresDsn

    # Server
    PORT: int = 8000

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
