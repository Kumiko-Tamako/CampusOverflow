from __future__ import annotations

from typing import Protocol


class PasswordHasher(Protocol):
    """密码哈希端口：application 定义，infrastructure 提供 bcrypt 实现。"""

    async def hash(self, plain: str) -> str:
        """将明文密码转为 bcrypt 哈希。"""
        ...
