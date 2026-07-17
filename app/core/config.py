from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Apify
    apify_token: str
    apify_google_maps_actor_id: str = "compass/crawler-google-places"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Google Sheets
    google_service_account_file: str = "credentials/google_service_account.json"
    google_sheet_id: str = ""

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    default_email_sender_name: str = "Your Name"
    # Crawler
    crawler_max_depth: int = 3
    crawler_max_pages: int = 15
    crawler_timeout_seconds: int = 10

    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()