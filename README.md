# Calvin AI Resume Assistant

基于真实 Markdown 资料的简历问答 Agent：Markdown → 切片 → OpenAI Embedding → ChromaDB → FastAPI → Next.js 聊天界面。

## 本地启动

1. 将 `backend/.env.example` 复制为 `backend/.env` 并填入 Key。
2. 后端：`uvicorn app.main:app --reload --port 8000`。
3. 首次索引：向 `POST /api/index` 发送请求。
4. 前端：复制 `.env.local.example` 为 `.env.local`，执行 `npm install`、`npm run dev`。

## 参考架构

- umbertogriffo/rag-chatbot：Markdown、Chroma、来源追溯与增量索引思路（Apache-2.0）。
- langchain-ai/langchain-nextjs-template：聊天界面与检索问答交互（MIT）。

本项目不复制第三方业务代码；实现针对个人简历知识库与 OpenAI API 自行编写。
