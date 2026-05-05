from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Audit AI"
    database_url: str = "sqlite:///./smart_audit.db"
    anthropic_api_key: str | None = None
    claude_model: str = "claude-3-5-sonnet-latest"
    enable_slither: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
