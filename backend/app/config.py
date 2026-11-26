from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://interview:interview@localhost:5432/interview_agent"
    redis_url: str = "redis://localhost:6379/0"

    # Provider selection is controlled centrally; no provider-specific code in agents.
    ai_provider: str = "gemini"
    google_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    cors_origins: str = "http://localhost:3000,http://localhost:8081"
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    @property
    def cors_origin_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
