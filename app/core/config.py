from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str = "AI Customer Support"
    APP_VERSION: str = "1.0.0"
    APP_V1_PREFIX: str = "/api/v1"

    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()