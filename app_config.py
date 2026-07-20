import os
from pathlib import Path
from typing import ClassVar, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_FOLDER = Path(__file__).parent

res = load_dotenv(_ROOT_FOLDER / ".env")

class AppConstants:
    TITLE: str = "Ai5elementApiBackend"
    RELEASE_DATE: str = "2026/07/20"
    VERSION: str = "1.0.0"
    LOGGER_NAME: str = "ai_5element_backend"


class ServerSettings(BaseModel):
    PORT: int = 5055


class DBSettings(BaseModel):
    FILENAME: str = os.environ.get("SQLITE_DB_FILE", "database.db")

    sync_url: str = ""
    async_url: str = ""

    ECHO: bool = True
    ECHO_POOL: bool = False
    POOL_SIZE: int = 50
    MAX_OVERFLOW: int = 10

    NAMING_KEYS_CONVENTION: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @model_validator(mode="after")
    def val_model_after(self) -> DBSettings:
        self.sync_url = f"sqlite:///{self.FILENAME}"
        self.async_url = f"sqlite+aiosqlite:///{self.FILENAME}"

        return self


class AuthenticationSettings(BaseModel):
    jwt_secret: str = "secret"
    jwt_refresh_secret: str = "refresh_secret"
    jwt_algorithm: str = "HS256"
    jwt_expires_min: int = 20
    jwt_refresh_expires_min: int = 60


class AppConfig(BaseSettings):

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=os.path.join(_ROOT_FOLDER, ".env"), case_sensitive=False, env_nested_delimiter="__"
    )

    llm_provider: Literal["ollama", "openai", "deepseek", "openrouter", "none"] = "none"
    llm_base_url: str = ""
    llm_model: str = ""
    llm_api_key: str = ""

    DB: DBSettings = DBSettings()
    SERVER: ServerSettings = ServerSettings()
    AUTH: AuthenticationSettings = AuthenticationSettings()

    @property
    def base_dir(self) -> str:
        return str(_ROOT_FOLDER)


app_settings: AppConfig = AppConfig()
