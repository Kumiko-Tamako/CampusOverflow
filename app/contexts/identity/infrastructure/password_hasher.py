from __future__ import annotations

import asyncio

import bcrypt

_ROUNDS = 12


class BcryptPasswordHasher:
    """PasswordHasher 端口的 bcrypt 实现。

    bcrypt 是 CPU 密集操作：通过 asyncio.to_thread 丢进线程池执行，
    避免单次哈希（100~300ms）阻塞整个事件循环。
    """

    async def hash(self, plain: str) -> str:
        salt = bcrypt.gensalt(rounds=_ROUNDS)
        digest = await asyncio.to_thread(bcrypt.hashpw, plain.encode("utf-8"), salt)
        return digest.decode("utf-8")

    async def verify(self, plain: str, hashed: str) -> bool:
        valid = await asyncio.to_thread(
            bcrypt.checkpw, plain.encode("utf-8"), hashed.encode("utf-8")
        )
        return bool(valid)
