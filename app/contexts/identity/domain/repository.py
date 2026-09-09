from __future__ import annotations

from typing import Protocol

from app.contexts.identity.domain.user import User


class UserRepository(Protocol):
    """用户聚合持久化端口：domain 定义接口，infrastructure 实现。"""

    async def get_by_email(self, email: str) -> User | None:
        """按邮箱查询用户。"""
        ...

    async def get_by_student_id(self, student_id: str) -> User | None:
        """按学号查询用户。"""
        ...

    async def get_by_staff_id(self, staff_id: str) -> User | None:
        """按工号查询用户。"""
        ...

    async def add(self, user: User) -> None:
        """新增用户（聚合整体落库）。"""
        ...
