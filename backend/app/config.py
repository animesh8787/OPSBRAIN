from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    upload_dir: str = "./uploads"
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "documents"
    firebase_project_id: str = ""
    firebase_service_account_file: str = ""
    firebase_service_account_json: str = ""
    max_upload_size_mb: int = 50
    allowed_upload_mime_types: list[str] = ["application/pdf"]
    cors_origins: list[str] = ["http://localhost:3000"]

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.1-8b-instant"

settings = Settings()