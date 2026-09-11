from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.contexts.qa.domain.question import Question


class QuestionRepository(Protocol):
    """问题聚合持久化端口：domain 定义接口，infrastructure 实现。"""

    async def add(self, question: Question) -> None:
        """新增问题（聚合整体落库）。"""
        ...

    async def get_by_id(self, question_id: UUID) -> Question | None:
        """按问题 ID 查询（2.4 集成测试回读使用，2.6 详情直接复用）。"""
        ...
