from app.config import settings
from app.services.documents import chunk_documents, load_markdown_documents


def test_knowledge_files_load_and_chunk() -> None:
    documents = load_markdown_documents(settings.knowledge_dir)
    chunks = chunk_documents(documents)
    assert len(documents) >= 7
    assert len(chunks) >= len(documents)
    assert {document.metadata["file"] for document in documents} >= {"internship.md", "product_projects.md"}
