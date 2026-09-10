"""测试全局 fixture。"""

from __future__ import annotations

import pytest


@pytest.fixture
async def redis_cleanup() -> None:
    """H 点：集成测试 teardown 时关闭并重建 Redis 客户端。

    pytest-asyncio 每测试一个事件循环，而 app 的 Redis 客户端是模块级单例；
    若不重建，连接会在旧 loop 失效后跨 loop 复用（与 engine NullPool 同源决策）。
    仅在需要 Redis 的测试（登录/刷新相关）显式请求本 fixture。
    """
    yield
    from app.shared.redis import get_redis, reset_redis

    client = get_redis()
    await client.aclose()
    reset_redis()
