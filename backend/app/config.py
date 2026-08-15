from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "backend" / ".env")


@dataclass(frozen=True)
class Settings:
    knowledge_dir: Path = PROJECT_ROOT / "knowledge"
    chroma_dir: Path = PROJECT_ROOT / "backend" / "data" / "chroma"
    collection_name: str = "resume_knowledge"
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
    allowed_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    @property
    def has_api_key(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))


settings = Settings()
