from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterCommand:
    """注册用例的输入命令。"""

    role: str
    email: str
    password: str
    student_id: str | None = None
    staff_id: str | None = None
