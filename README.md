# Calvin AI Resume Assistant

一个基于真实 Markdown 简历资料的招聘问答 Demo。回答链路为：知识库切片 → 通义千问 Embedding 检索 → ChromaDB → 通义千问回答。

## 面试官体验入口

线上生产页面使用 `public/index.html`，请求同域的 `POST /api/chat`。`frontend/` 是保留的 Next.js 原型，不是当前 Vercel 生产入口。

## 本地运行

1. 复制 `backend/.env.example` 为 `backend/.env`，填入阿里云百炼的 `DASHSCOPE_API_KEY`。
2. 在项目根目录执行：

   ```bash
   pip install -r requirements-dev.txt
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

3. 打开 `http://localhost:8000`。首次提问会自动建立向量索引；无需暴露单独的索引接口。
4. 运行测试：在项目根目录执行 `pytest backend/tests`。

## Vercel 部署

1. 从 GitHub 导入本仓库，Root Directory 保持为空。
2. 添加加密环境变量 `DASHSCOPE_API_KEY`，仅用于 Production/Preview。
3. Deploy。Vercel 会将全部网页和 API 请求交给 `api/index.py` 中的 FastAPI 应用处理。

Vercel 函数实例的磁盘是临时的。重启后首次问答会重新构建 Chroma 索引，因此该版本定位为小流量求职展示 Demo，而非高并发生产服务。

## 安全边界

- `.env` 与 Chroma 本地数据均被 Git 忽略。
- 不提供公开的索引重建接口，避免任意访客触发 Embedding 成本。
- 当知识库无法支持回答时，模型应明确说明信息不足，不编造。

