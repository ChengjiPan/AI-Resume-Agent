from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "backend" / ".env")

# Vercel functions can only write to /tmp. On a local or Render deployment we
# keep the original project-local location instead.
DEFAULT_CHROMA_DIR = (
    Path("/tmp") / "ai_resume_chroma"
    if os.getenv("VERCEL")
    else PROJECT_ROOT / "backend" / "data" / "chroma"
)


@dataclass(frozen=True)
class Settings:
    knowledge_dir: Path = PROJECT_ROOT / "knowledge"
    chroma_dir: Path = Path(os.getenv("CHROMA_DIR", str(DEFAULT_CHROMA_DIR)))
    # A separate collection avoids mixing vectors from the previous OpenAI index.
    collection_name: str = "resume_knowledge_qwen_v1"
    api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    base_url: str = os.getenv(
        "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    embedding_model: str = os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v4")
    chat_model: str = os.getenv("QWEN_CHAT_MODEL", "qwen-plus")
    allowed_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key)


settings = Settings()

