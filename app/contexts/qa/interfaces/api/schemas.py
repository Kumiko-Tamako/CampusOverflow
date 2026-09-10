from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AskQuestionRequest(BaseModel):
    """POST /api/v1/questions 请求体。

    str_strip_whitespace 在长度约束之前生效：纯空白标题/正文 strip 后为空 → 422。
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1, max_length=5000)


class QuestionResponse(BaseModel):
    """问题响应白名单：不含任何内部字段。"""

    id: UUID
    title: str
    body: str
    author_id: UUID
    created_at: datetime
