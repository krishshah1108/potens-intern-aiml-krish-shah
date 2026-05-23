"""Application configuration loaded from environment."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    chroma_persist_dir: str = "chroma_db"
    documents_dir: str = "documents"
    collection_name: str = "potens_docs"
    top_k: int = 8
    retrieval_candidates: int = 25
    similarity_threshold: float = 0.45
    chunk_size: int = 800
    chunk_overlap: int = 150
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    @property
    def chroma_path(self) -> Path:
        return PROJECT_ROOT / self.chroma_persist_dir

    @property
    def docs_path(self) -> Path:
        return PROJECT_ROOT / self.documents_dir

    @property
    def interaction_log_path(self) -> Path:
        """Full Q&A traces from POST /ask (outside app/ for easy access)."""
        return PROJECT_ROOT / "evaluation" / "eval_dataset.json"


settings = Settings()
