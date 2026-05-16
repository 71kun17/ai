# 进度日志

## 会话：2026-05-14

### 阶段 1：需求与发现
- **状态：** complete
- 执行的操作：读取知乎文章，确定规模/场景/技术栈
- 创建/修改的文件：task_plan.md, findings.md, progress.md

### 阶段 2：规划与结构
- **状态：** complete
- 执行的操作：编写10-task实施计划，创建项目文档
- 创建/修改的文件：docs/superpowers/plans/2026-05-14-ai-customer-service.md, README.md

## 会话：2026-05-15

### 阶段 3：实现
- **状态：** in_progress

#### Task 1: 项目骨架搭建 ✅
- 创建 backend/ 目录结构，frontend/ 目录结构
- 安装Python虚拟环境及所有依赖
- FastAPI主入口 + 配置管理
- Vue 3 + Element Plus脚手架（手动创建）
- 创建/修改的文件：
  - backend/requirements.txt ✅
  - backend/app/config.py ✅
  - backend/app/main.py ✅
  - frontend/package.json ✅
  - frontend/vite.config.ts ✅
  - frontend/tsconfig.json ✅
  - frontend/index.html ✅
  - frontend/src/main.ts ✅
  - frontend/src/App.vue ✅
  - frontend/src/vite-env.d.ts ✅
  - frontend/src/router/index.ts ✅
  - frontend/src/api/index.ts ✅

#### Task 2: 数据库模型与知识库CRUD ✅
- SQLAlchemy ORM模型（Knowledge, Conversation, AnalyticsLog）
- 知识库CRUD API（列表/创建/读取/更新/删除/分类）
- 创建/修改的文件：
  - backend/app/models/database.py ✅
  - backend/app/models/knowledge.py ✅
  - backend/app/models/conversation.py ✅
  - backend/app/api/knowledge.py ✅

#### Task 3: 向量检索与语义匹配 ✅
- scikit-learn TF-IDF + 余弦相似度替代ChromaDB
- 向量索引持久化（pickle）
- 启动时自动从数据库重建索引
- 创建/修改的文件：
  - backend/app/services/vector_store.py ✅

#### Task 4: LLM意图识别与实体抽取 ✅
- 通义千问API封装 + 本地关键词回退
- 10种电商意图分类 + 实体抽取
- 创建/修改的文件：
  - backend/app/services/nlp.py ✅

#### Task 5: 对话引擎RAG ✅
- 检索增强生成流程（向量检索→LLM生成）
- 多轮对话上下文管理
- 转人工判定逻辑
- 无API Key时自动回退到检索式回答
- 创建/修改的文件：
  - backend/app/services/dialog.py ✅
  - backend/app/api/chat.py ✅

#### Task 6: 数据分析看板API ✅
- 概览指标、意图分布、每日趋势、热点词、最近会话
- 创建/修改的文件：
  - backend/app/api/analytics.py ✅

#### Task 7: 前端管理后台 ✅
- AdminLayout（侧边栏 + 顶栏）
- Dashboard（统计卡片 + 饼图 + 折线图）
- KnowledgeList（搜索/筛选/分页表格）
- KnowledgeEdit（表单创建/编辑）
- Conversations（会话列表 + 详情弹窗）
- 创建/修改的文件：
  - frontend/src/layouts/AdminLayout.vue ✅
  - frontend/src/views/admin/Dashboard.vue ✅
  - frontend/src/views/admin/KnowledgeList.vue ✅
  - frontend/src/views/admin/KnowledgeEdit.vue ✅
  - frontend/src/views/admin/Conversations.vue ✅

#### Task 8: 前端用户聊天界面 ✅
- 电商风格聊天窗口
- Markdown渲染 + 快捷问题 + 转人工
- 知识来源引用展示
- 创建/修改的文件：
  - frontend/src/views/ChatWidget.vue ✅

#### Task 9: 种子数据与端到端验证 ⏳
- 10条电商FAQ种子数据已导入
- 创建/修改的文件：
  - backend/scripts/seed_data.py ✅
  - backend/.env ✅
- ⚠ 待前端npm install后做端到端验证

## 测试结果
| 测试 | 状态 |
|------|------|
| 后端应用导入 | ✅ PASS (10 docs in vector store) |
| 种子数据导入 | ✅ PASS (10条) |
| 前端编译 | ⏳ 需要 npm install |

## 错误日志
| 时间戳 | 错误 | 解决方案 |
|--------|------|---------|
| 2026-05-14 | Zhihu 403 | 用户粘贴文章内容 |
| 2026-05-14 | Python未安装 | 使用Codex内置Python |
| 2026-05-14 | ChromaDB需要C++编译 | 替换为scikit-learn |
| 2026-05-15 | 数据库相对路径不匹配 | 改为绝对路径 |
| 2026-05-15 | 提权审批系统内部错误 | 用户手动运行外部命令 |

## 五问重启检查
| 问题 | 答案 |
|------|------|
| 我在哪里？ | Task 9：待前端安装+验证 |
| 我要去哪里？ | npm install → 启动验证 → 完成 |
| 目标是什么？ | 电商智能客服全栈Web应用 |
| 我学到了什么？ | 见 findings.md |
| 我做了什么？ | 后端全部完成 + 前端页面完成 |
