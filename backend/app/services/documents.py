from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


HEADERS = [("#", "title"), ("##", "section"), ("###", "subsection")]


def load_markdown_documents(knowledge_dir: Path) -> list[Document]:
    """Load only the approved Markdown knowledge base, with file/heading metadata."""
    if not knowledge_dir.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {knowledge_dir}")

    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS, strip_headers=False)
    documents: list[Document] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        for document in header_splitter.split_text(text):
            document.metadata["file"] = path.name
            document.metadata.setdefault("section", document.metadata.get("title", path.stem))
            documents.append(document)
    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Convert long sections into small, overlapping passages for precise retrieval."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120)
    return splitter.split_documents(documents)
