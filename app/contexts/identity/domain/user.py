from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from app.contexts.identity.domain.errors import IdentityRequiredError, WeakPasswordError
from app.contexts.identity.domain.value_objects import Email, PasswordHash, StaffId, StudentId

Role = Literal["student", "teacher"]

_PASSWORD_MIN_LENGTH = 8
_HAS_LETTER = re.compile(r"[A-Za-z]")
_HAS_DIGIT = re.compile(r"\d")


def validate_password_strength(plain: str) -> None:
    """密码强度不变式：至少 8 位且同时含字母和数字（US-R04）。"""
    too_short = len(plain) < _PASSWORD_MIN_LENGTH
    if too_short or not _HAS_LETTER.search(plain) or not _HAS_DIGIT.search(plain):
        raise WeakPasswordError("密码至少 8 位且需同时包含字母和数字")


@dataclass(frozen=True, slots=True)
class UserRegistered:
    """领域事件：用户注册完成。"""

    user_id: UUID
    role: str
    occurred_at: datetime


@dataclass
class User:
    """用户聚合根：学生或教师，身份二选一（不变式 4）。"""

    id: UUID
    role: Role
    email: Email
    password_hash: PasswordHash
    student_id: StudentId | None
    staff_id: StaffId | None
    created_at: datetime
    events: list[UserRegistered] = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def register(
        cls,
        *,
        role: Role,
        email_value: str,
        password_hash_value: str,
        identity_value: str | None,
    ) -> User:
        student_id: StudentId | None = None
        staff_id: StaffId | None = None

        if role == "student":
            if identity_value is None:
                raise IdentityRequiredError("学生注册必须提供学号")
            student_id = StudentId(identity_value)
        elif role == "teacher":
            if identity_value is None:
                raise IdentityRequiredError("教师注册必须提供工号")
            staff_id = StaffId(identity_value)

        now = datetime.now(UTC)
        user = cls(
            id=uuid4(),
            role=role,
            email=Email(email_value),
            password_hash=PasswordHash(password_hash_value),
            student_id=student_id,
            staff_id=staff_id,
            created_at=now,
        )
        user.events.append(UserRegistered(user_id=user.id, role=role, occurred_at=now))
        return user
