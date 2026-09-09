from collections.abc import AsyncIterator

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings


def _build_engine() -> AsyncEngine:
    settings = get_settings()
    # NullPool：不复用连接。代价是每次请求新建连接（本机 ~1ms），
    # 换取对 pytest 多事件循环 / uvicorn --reload 的免疫，阶段 4 上线前再评估连接池。
    return create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )


engine = _build_engine()
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
