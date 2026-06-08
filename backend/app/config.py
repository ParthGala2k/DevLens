"""Application settings, loaded from environment variables.

All configuration flows through this module (pydantic-settings). Never read os.environ
directly elsewhere — import `settings` from here so config stays centralized and typed.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Google Cloud / Gemini ---
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    google_genai_use_vertexai: bool = True
    gemini_model: str = "gemini-3-pro"

    # --- BigQuery (Fivetran sync target) ---
    bigquery_project: str = ""
    bigquery_dataset_gitlab: str = "gitlab"
    bigquery_dataset_jira: str = "jira"
    bigquery_dataset_slack: str = "slack"
    bigquery_dataset_calendar: str = "calendar"
    bigquery_dataset_pagerduty: str = "pagerduty"
    bigquery_dataset_metrics: str = "devlens_metrics"

    # --- Firestore ---
    firestore_project: str = ""
    firestore_database: str = "(default)"

    # --- Fivetran MCP (sync layer — mandatory track integration) ---
    fivetran_mcp_url: str = ""
    fivetran_api_key: str = ""
    fivetran_api_secret: str = ""
    fivetran_group_id: str = ""

    # --- GitLab MCP (action layer — create/assign/label issues) ---
    gitlab_mcp_url: str = ""
    gitlab_token: str = ""
    gitlab_project_id: str = ""

    # --- Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
