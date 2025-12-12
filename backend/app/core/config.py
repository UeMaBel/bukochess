from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Bukochess Backend"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
