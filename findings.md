# 发现与决策

## 需求
- 构建电商AI智能客服系统（中小型企业版MVP）
- 核心功能：意图识别、FAQ知识库、多轮对话、人机协同、数据分析
- 全栈Web应用：用户聊天界面 + 管理后台
- 新增：多平台全自动回复（虾皮、亚马逊）

## 多平台集成研究发现

### 虾皮 (Shopee) API
- Open API v2 Chat 接口可用
- 端点：get_message_list, send_message, upload_image
- 鉴权：OAuth 2.0 (partner_id + partner_key + access_token)
- 限流：基础版 ~1000次/天
- 签名：HMAC-SHA256 (partner_id + timestamp + access_token + body)
- 文档：https://open.shopee.com/

### 亚马逊 (Amazon) API
- SP-API Messaging API v1
- 端点：getMessagingActionsForOrder, createResponse系列
- 鉴权：AWS IAM + LWAAuthorizationCredentials
- 支持 SQS 通知队列（实时推送）
- 文档：https://developer-docs.amazon.com/sp-api/

### 技术决策
| 决策 | 理由 |
|------|------|
| 适配器模式 | 统一接口，后续加平台只需实现新Adapter |
| 轮询先行 | 第1期轮询（30s间隔），第2期切Webhook |
| 置信度分流 | kb_score*0.6 + (1-handoff_risk)*0.4，阈值0.7 |
| 连续3次低分挂起 | 避免LLM幻想激怒买家 |
| 复用RAG_PROMPTS | 七国语言prompt已就绪 |
| FastAPI | Python NLP生态成熟，异步支持好 |
| SQLite | 轻量零运维，适合中小型MVP |
| 检索增强生成(RAG) | 结合知识库检索+LLM生成，减少幻觉 |

## 资源
- 通义千问API文档：https://help.aliyun.com/zh/model-studio/
- 虾皮开放平台：https://open.shopee.com/
- 亚马逊SP-API：https://developer-docs.amazon.com/sp-api/

## 视觉/浏览器发现
- 无