"""自动回复引擎：置信度计算、分流决策、消息发送"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.dialog import generate_answer, should_handoff
from app.services.platform_adapter import BasePlatformAdapter, PlatformMessage, ReplyResult
from app.models.database import SessionLocal
from app.models.platform import PlatformMessage as PM, AutoReplyLog


CONFIDENCE_THRESHOLD = 0.7
MAX_CONSECUTIVE_LOW = 3


class AutoReplyEngine:
    """
    自动回复引擎
    - 调用 RAG 引擎生成回复
    - 计算置信度
    - 高置信度：自动发送
    - 低置信度：写入审核队列
    """

    def __init__(self, threshold: float = CONFIDENCE_THRESHOLD):
        self.threshold = threshold
        self._consecutive_low: dict[str, int] = {}

    async def process_message(
        self,
        msg: PlatformMessage,
        adapter: BasePlatformAdapter
    ) -> ReplyResult:
        """处理一条买家消息"""
        db = SessionLocal()
        try:
            intent = {"intent": "", "entities": [], "confidence": 0.0}

            history = self._get_history(db, msg.conversation_id)

            result = await generate_answer(
                user_message=msg.content,
                intent=intent,
                history=history,
                lang=self._detect_lang(msg.content)
            )

            kb_score = self._calc_kb_score(result)
            handoff = await should_handoff(msg.content, 0, self._detect_lang(msg.content))
            intent_score = 0.5
            final_confidence = kb_score * 0.6 + (1 - int(handoff)) * 0.4

            reply = ReplyResult(
                message_id=msg.message_id,
                answer=result["answer"],
                kb_score=kb_score,
                intent_score=intent_score,
                final_confidence=final_confidence,
                sources=result.get("sources", []),
                handoff=handoff
            )

            conv_key = f"{msg.platform}:{msg.conversation_id}"

            if handoff or final_confidence < self.threshold:
                self._consecutive_low[conv_key] = self._consecutive_low.get(conv_key, 0) + 1
                if self._consecutive_low[conv_key] >= MAX_CONSECUTIVE_LOW:
                    reply.handoff = True

                self._save_platform_message(db, msg, "pending_review")
                self._save_reply_log(db, msg, reply, "pending_review")
            else:
                self._consecutive_low[conv_key] = 0
                success = await adapter.send_message(msg.conversation_id, reply.answer)
                status = "auto_replied" if success else "pending_review"
                self._save_platform_message(db, msg, status)
                self._save_reply_log(db, msg, reply, status)
                if success:
                    await adapter.mark_read(msg.conversation_id)

            db.commit()
            return reply

        except Exception as e:
            db.rollback()
            print(f"[AutoReplyEngine] process_message error: {e}")
            return ReplyResult(
                message_id=msg.message_id,
                answer="",
                kb_score=0,
                intent_score=0,
                final_confidence=0,
                handoff=True
            )
        finally:
            db.close()

    def _calc_kb_score(self, result: dict) -> float:
        """从 RAG 结果计算知识库匹配分"""
        sources = result.get("sources", [])
        if not sources:
            return 0.0
        return max(s.get("similarity", 0) for s in sources)

    def _detect_lang(self, text: str) -> str:
        """简单语言检测"""
        has_cjk = any(
            '\u4e00' <= c <= '\u9fff'
            or '\u3040' <= c <= '\u309f'
            or '\uac00' <= c <= '\ud7af'
            for c in text
        )
        if has_cjk:
            has_hiragana = any('\u3040' <= c <= '\u309f' for c in text)
            if has_hiragana:
                return "ja"
            has_hangul = any('\uac00' <= c <= '\ud7af' for c in text)
            if has_hangul:
                return "ko"
            return "zh"
        return "en"

    def _get_history(self, db: Session, conversation_id: str, limit: int = 6) -> list:
        """获取会话历史"""
        msgs = db.query(PM).filter(
            PM.conversation_id == conversation_id
        ).order_by(PM.created_at.desc()).limit(limit).all()
        return [
            {"role": "user" if m.sender == "buyer" else "assistant", "content": m.content}
            for m in reversed(msgs)
        ]

    def _save_platform_message(self, db: Session, msg: PlatformMessage, status: str):
        """存储平台消息"""
        existing = db.query(PM).filter(PM.message_id == msg.message_id).first()
        if existing:
            existing.status = status
            return
        record = PM(
            platform=msg.platform,
            conversation_id=msg.conversation_id,
            message_id=msg.message_id,
            sender=msg.sender,
            content=msg.content,
            buyer_name=msg.buyer_name,
            order_id=msg.order_id or "",
            raw_data=msg.raw_data,
            status=status
        )
        db.add(record)

    def _save_reply_log(self, db: Session, msg: PlatformMessage, reply: ReplyResult, action: str):
        """存储回复日志"""
        log = AutoReplyLog(
            platform=msg.platform,
            conversation_id=msg.conversation_id,
            message_id=msg.message_id,
            buyer_message=msg.content,
            reply_content=reply.answer,
            kb_score=reply.kb_score,
            intent_score=reply.intent_score,
            final_confidence=reply.final_confidence,
            action=action,
            handoff=reply.handoff
        )
        db.add(log)