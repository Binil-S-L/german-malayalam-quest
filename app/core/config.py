from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://quest:quest@localhost:5432/quest_dev"
    TEST_DATABASE_URL: str = "postgresql+psycopg://quest_test:quest_test@localhost:5433/quest_test"
    APP_ENV: str = "development"


settings = Settings()
