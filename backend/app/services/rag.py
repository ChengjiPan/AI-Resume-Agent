from __future__ import annotations

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import Settings
from app.services.documents import chunk_documents, load_markdown_documents


SYSTEM_PROMPT = """你是 Calvin AI Resume Assistant。只根据提供的个人知识库回答。
如果资料不足、存在版本冲突或无法确认，请明确说明，不要编造。
回答使用中文，优先说明项目背景、候选人角色、方法、结果与产品价值；保持简洁、适合招聘经理阅读。"""


def _embeddings(settings: Settings) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )


def index_knowledge_base(settings: Settings) -> tuple[int, int]:
    documents = load_markdown_documents(settings.knowledge_dir)
    chunks = chunk_documents(documents)
    if not chunks:
        raise ValueError("No readable Markdown content was found in the knowledge directory.")
    if settings.chroma_dir.exists():
        shutil.rmtree(settings.chroma_dir)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    Chroma.from_documents(
        documents=chunks,
        embedding=_embeddings(settings),
        collection_name=settings.collection_name,
        persist_directory=str(settings.chroma_dir),
    )
    return len(documents), len(chunks)


def _store_exists(chroma_dir: Path) -> bool:
    return chroma_dir.exists() and any(chroma_dir.iterdir())


def answer_question(question: str, settings: Settings) -> tuple[str, list[dict[str, str | None]]]:
    if not _store_exists(settings.chroma_dir):
        # Free hosting instances can restart and lose local vector data. The source
        # Markdown remains bundled with the app, so rebuild on the first question.
        index_knowledge_base(settings)
    store = Chroma(
        collection_name=settings.collection_name,
        persist_directory=str(settings.chroma_dir),
        embedding_function=_embeddings(settings),
    )
    passages = store.similarity_search(question, k=4)
    if not passages:
        return "现有知识库中没有找到足够相关的资料。", []
    context = "\n\n".join(f"[来源：{doc.metadata.get('file')}]\n{doc.page_content}" for doc in passages)
    response = ChatOpenAI(
        model=settings.chat_model,
        temperature=0.2,
        api_key=settings.api_key,
        base_url=settings.base_url,
    ).invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"知识库：\n{context}\n\n问题：{question}")]
    )
    sources = [
        {"file": str(doc.metadata.get("file", "未知文件")), "section": doc.metadata.get("section")}
        for doc in passages
    ]
    unique_sources = list({(item["file"], item["section"]): item for item in sources}.values())
    return str(response.content), unique_sources

