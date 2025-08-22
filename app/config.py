from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv

# Load .env early so environment is available for Settings
load_dotenv()


class Settings(BaseSettings):
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    google_cse_id: str = Field(default="", alias="GOOGLE_CSE_ID")

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    openrouter_model: str = Field(default="google/gemini-2.5-pro", alias="OPENROUTER_MODEL")

    request_timeout_seconds: int = Field(default=15, alias="REQUEST_TIMEOUT_SECONDS")
    llm_timeout_seconds: int = Field(default=25, alias="LLM_TIMEOUT_SECONDS")
    agent_max_steps: int = Field(default=6, alias="AGENT_MAX_STEPS")
    user_agent: str = Field(default="AI-Researcher/0.1 (+https://open-webui/openapi-servers)", alias="USER_AGENT")

    search_ttl_seconds: int = Field(default=900, alias="SEARCH_TTL_SECONDS")

    api_token: str = Field(default="", alias="API_TOKEN")

    # pydantic-settings v2 config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore
