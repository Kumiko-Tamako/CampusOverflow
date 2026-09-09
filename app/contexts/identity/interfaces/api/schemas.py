from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class RegisterRequest(BaseModel):
    """POST /api/v1/auth/register 请求体。"""

    role: Literal["student", "teacher"]
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)
    student_id: str | None = Field(default=None, max_length=32)
    staff_id: str | None = Field(default=None, max_length=32)

    @model_validator(mode="after")
    def _identity_matches_role(self) -> RegisterRequest:
        if self.role == "student" and not self.student_id:
            raise ValueError("学生注册必须提供 student_id")
        if self.role == "teacher" and not self.staff_id:
            raise ValueError("教师注册必须提供 staff_id")
        return self


class RegisterResponse(BaseModel):
    """注册响应：绝不包含密码任何形态。"""

    id: UUID
    role: str
    email: str
    student_id: str | None
    staff_id: str | None
    created_at: datetime
