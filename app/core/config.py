from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str = "AI Customer Support"
    APP_VERSION: str = "1.0.0"
    APP_V1_PREFIX: str = "/api/v1"

    ENVIRONMENT: str = "development"

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "ai_customer_support"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()