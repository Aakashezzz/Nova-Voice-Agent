from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Nova Voice Agent"
    APP_VERSION: str = "0.1.0"

    LOG_LEVEL: str = "INFO"

    GROQ_API_KEY: str = ""

    OLLAMA_HOST: str = "http://localhost:11434"

    WHISPER_MODEL: str = "base"

    PIPER_MODEL: str = ""

    DATABASE_URL: str = "sqlite:///nova_voice.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()