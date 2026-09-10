from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from app.shared.redis import get_redis


class RedisRefreshTokenStore:
    """RefreshTokenStore 端口的 Redis 实现。

    - key：refresh:{jti} → user_id，EX TTL 自动过期
    - consume 用 GETDEL 原子"校验并消耗"：并发重放仅一次成功（轮换安全）
    - revoke 用 DEL，幂等
    - 每次操作动态取 get_redis() 当前单例：测试 reset_redis() 后新实例立即可见，
      避免缓存旧 client 引用导致跨事件循环复用已关闭连接
    """

    _PREFIX = "refresh:"

    async def save(self, jti: UUID, user_id: UUID, ttl: timedelta) -> None:
        await get_redis().set(
            f"{self._PREFIX}{jti}",
            str(user_id),
            ex=int(ttl.total_seconds()),
        )

    async def consume(self, jti: UUID) -> UUID | None:
        raw = await get_redis().getdel(f"{self._PREFIX}{jti}")
        return UUID(raw) if raw is not None else None

    async def revoke(self, jti: UUID) -> None:
        await get_redis().delete(f"{self._PREFIX}{jti}")
