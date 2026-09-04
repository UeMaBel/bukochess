from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Bukochess Backend"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True
    # Only required when the OpenAI engine is selected.
    openai_api_key: SecretStr = SecretStr("")

settings = Settings()
