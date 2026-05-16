# 🛒 电商智能客服系统

面向电商场景的AI智能客服全栈Web应用，基于检索增强生成（RAG）架构。

## 功能模块

- **智能对话** — 意图识别 + 实体抽取 + RAG生成回答
- **知识库管理** — FAQ CRUD + 语义检索 + 分类管理
- **多轮对话** — 上下文记忆 + 对话状态跟踪
- **人机协同** — 自动转人工 + 敏感词检测
- **数据分析** — 概览指标 + 意图分布 + 每日趋势

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI (Python 3.12) |
| 数据库 | SQLite + SQLAlchemy ORM |
| 向量检索 | scikit-learn TF-IDF + 余弦相似度 |
| AI引擎 | 通义千问API (qwen-plus) |
| 前端 | Vue 3 + Element Plus + Vite + TypeScript |

## 快速启动

### 后端

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 配置API密钥
echo LLM_API_KEY=your-key > .env

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 访问

- 用户聊天界面: http://localhost:5173/
- 管理后台: http://localhost:5173/admin
- API文档: http://localhost:8000/docs

## 项目结构

```
backend/
  app/
    api/          # API路由（knowledge, chat, analytics）
    core/         # 核心工具
    models/       # SQLAlchemy数据模型
    services/     # 业务逻辑（nlp, dialog, embedding, vector_store）
    config.py     # 配置管理
    main.py       # 应用入口
  data/           # SQLite数据库 + 向量索引
  scripts/        # 工具脚本
  tests/          # 测试
frontend/
  src/
    views/        # 页面组件
    admin/        # 管理后台页面
    api/          # API封装
    router/       # 路由配置
    layouts/      # 布局组件
```

## License

MIT
