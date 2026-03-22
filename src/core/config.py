from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env", 
        env_file_encoding="utf-8", 
        env_ignore_empty=True,
        extra="ignore"
    )

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
    
    # SQLite for development
    DATABASE_URL: str = "sqlite:///./users.db"
    
    # PostgreSQL for production (optional for dev)
    POSTGRES_SCHEME: str = "postgres+psycopg"
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_SERVER: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ""
    
    @computed_field
    @property
    def server_host(self) -> str:
       if self.ENVIRONMENT == "dev":
           return f"http://{self.DOMAIN}"
       return f"https://{self.DOMAIN}"
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str | PostgresDsn:
        if self.ENVIRONMENT == "dev":
            return self.DATABASE_URL
        else:
            return MultiHostUrl.build(
                scheme=self.POSTGRES_SCHEME,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )

settings = Settings() #type: ignore