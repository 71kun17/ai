# 任务计划：多平台全自动客服集成

## 目标
基于现有FastAPI后端，通过适配器模式接驳虾皮和亚马逊消息API，实现AI全自动回复。按置信度分流。

## 当前阶段
阶段 5：前端管理面板

## 各阶段

### 阶段 1：适配器架构搭建 ✅
- [x] 创建 BasePlatformAdapter 抽象基类
- [x] 创建 PlatformConfig/PlatformMessage/AutoReplyLog 模型
- [x] 数据库迁移（新增三张表）
- [x] 平台管理 API 骨架
- **状态：** complete

### 阶段 2：虾皮适配器实现 ✅
- [x] 创建 ShopeeAdapter（HMAC-SHA256签名、OAuth token刷新）
- [x] 消息拉取（get_message_list）/ 发送（send_message）
- [x] 平台配置 CRUD API
- **状态：** complete

### 阶段 3：自动回复引擎 ✅
- [x] 创建 auto_reply.py（AutoReplyEngine）
- [x] 置信度计算：kb_score*0.6 + (1-handoff_risk)*0.4
- [x] 高置信度→自动发送；低置信度→入审核队列
- [x] 连续3次低分或投诉关键词→挂起会话
- [x] 语言自动检测（zh/en/ja/ko）
- **状态：** complete

### 阶段 4：后台轮询 + 启动集成 ✅
- [x] FastAPI startup 事件启动轮询任务
- [x] 每个active平台一个asyncio循环
- [x] 新消息→自动回复引擎→发送或入队
- [x] shutdown 事件优雅停止
- **状态：** complete

### 阶段 5：前端管理面板
- [ ] 侧边栏新增「平台管理」菜单
- [ ] 虾皮API凭证配置页
- [ ] 待审核消息列表页（批准/拒绝）
- [ ] 自动回复统计看板
- **状态：** in_progress

### 阶段 6：端到端测试
- [ ] 单元测试：适配器签名、token刷新
- [ ] 集成测试：消息流→自动回复→分流
- [ ] Mock API链路测试
- **状态：** pending

## 已做决策
| 决策 | 理由 |
|------|------|
| 适配器模式 | 后续加平台只需写新Adapter |
| 轮询→Webhook | 轮询实现快，后期切实时 |
| SQLite新增表 | 与现有架构一致 |
| 置信度阈值 0.7 | 保守起步，管理后台可调 |

## 备注
- 置信度阈值默认0.7，可通过管理后台调整
- 审核队列消息超过24小时自动转人工标签
- 第1期不做图片消息处理