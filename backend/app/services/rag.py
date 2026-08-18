from __future__ import annotations

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import Settings
from app.services.documents import chunk_documents, load_markdown_documents


SYSTEM_PROMPT = """你是 Calvin AI Resume Assistant。只根据提供的个人知识库回答。
如果资料不足、存在版本冲突或无法确认，请明确说明，不要编造，也不要补充知识库中没有的数据、职责或结论。

当问题涉及某一段具体实习或项目时，必须使用下面的六项结构；没有资料的项目要明确写“资料未提供”：
1. 项目背景
2. 我的角色
3. 我的任务
4. 使用的方法
5. 数据结果
6. 产品价值

当问题是能力、教育或职业优势等概述类问题时，使用清晰的要点回答，并把每项判断和已提供资料对应。回答使用中文，简洁、专业、适合招聘经理阅读。"""


def _embeddings(settings: Settings) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        # DashScope accepts source text, not LangChain's pre-tokenized integer arrays.
        check_embedding_ctx_length=False,
        # text-embedding-v4 accepts at most 10 strings per request.
        chunk_size=10,
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
        {
            "file": str(doc.metadata.get("file", "未知文件")),
            "section": doc.metadata.get("section"),
            # A short original excerpt lets the recruiter verify that the answer
            # is grounded without exposing the whole knowledge-base document.
            "excerpt": " ".join(doc.page_content.split())[:220],
        }
        for doc in passages
    ]
    unique_sources = []
    seen_sources = set()
    for item in sources:
        identity = (item["file"], item["section"])
        if identity not in seen_sources:
            unique_sources.append(item)
            seen_sources.add(identity)
    return str(response.content), unique_sources
