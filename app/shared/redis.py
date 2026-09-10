from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis

from app.config.settings import get_settings

_redis: Redis | None = None


def get_redis() -> Redis:
    """Redis 客户端惰性单例。

    模块级复用连接（uvicorn 单事件循环下正确）；测试通过 reset_redis 重建，
    避免 pytest 多事件循环下连接跨 loop 复用（与 engine.py NullPool 同源决策）。
    """
    global _redis
    if _redis is None:
        from redis.asyncio import Redis

        _redis = Redis.from_url(get_settings().redis_url, decode_responses=True)
    return _redis


def reset_redis() -> None:
    """丢弃客户端引用（测试清理用）；调用方需先 await aclose()。"""
    global _redis
    _redis = None
