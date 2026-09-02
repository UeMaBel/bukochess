from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    app_name: str = "Bukochess Backend"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True
    openai_api_key: SecretStr

    class Config:
        env_file = ".env"


settings = Settings()
