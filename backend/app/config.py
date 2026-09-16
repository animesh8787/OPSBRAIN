import json

from pydantic import Field
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

    # Embeddings run through HF's hosted Inference API rather than a local
    # sentence-transformers model - loading BAAI/bge-large-en-v1.5 locally
    # (or even the smallest viable alternative) needs ~500MB+ RSS just for
    # torch + the model weights, which alone exceeds Render's free-tier
    # 512MB limit before the rest of the app even loads. Get a free token
    # at huggingface.co/settings/tokens (read access is enough).
    hf_token: str = ""
    embedding_model: str = "BAAI/bge-large-en-v1.5"

    # Plain string, not list[str]: pydantic-settings tries to JSON-decode any
    # list-typed field's raw env value, which raises on a blank env var (left
    # unset in .env, or an empty dashboard field on Render) instead of falling
    # back to the default - crashing the whole app at startup. Parsing it
    # ourselves via the cors_origins property sidesteps that entirely.
    cors_origins_json: str = Field(default="", validation_alias="CORS_ORIGINS")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-20b"

    @property
    def cors_origins(self) -> list[str]:
        if not self.cors_origins_json.strip():
            return ["http://localhost:3000"]
        return json.loads(self.cors_origins_json)

settings = Settings()
