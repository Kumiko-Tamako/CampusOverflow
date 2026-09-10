"""BodyLimitMiddleware 测试：413 拦截不碰数据库，进 CI（修复暴力测试 E-06）。

覆盖两种发送形态：带 Content-Length 的超大 body、chunked 流式（无 Content-Length）——
后者正是 E-06 修复所针对的绕过面。
"""

import json

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.shared.body_limit import MAX_BODY_BYTES


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=create_app()), base_url="http://test")


async def test_oversize_body_with_content_length_returns_413() -> None:
    async with _client() as client:
        resp = await client.post(
            "/api/v1/auth/register",
            content=b"x" * (MAX_BODY_BYTES + 1),
            headers={"content-type": "application/json"},
        )
    assert resp.status_code == 413
    assert resp.json() == {"detail": "request body too large"}


async def test_oversize_chunked_body_without_content_length_returns_413() -> None:
    async def huge_stream():
        yield b"x" * (MAX_BODY_BYTES + 1)

    async with _client() as client:
        resp = await client.post(
            "/api/v1/auth/register",
            content=huge_stream(),
            headers={"content-type": "application/json"},
        )
    assert resp.status_code == 413
    assert resp.json() == {"detail": "request body too large"}


async def test_small_body_passes_through_to_validation() -> None:
    """小 body 正常重放：请求进入路由层，由 Pydantic 判 422（非中间件 413）。"""
    async with _client() as client:
        resp = await client.post(
            "/api/v1/auth/register",
            content=json.dumps({"role": "student", "email": "a@b.cn", "password": "x"}),
            headers={"content-type": "application/json"},
        )
    assert resp.status_code == 422  # 缺 student_id 等——证明 body 完整到达路由


async def test_health_get_passes_through() -> None:
    async with _client() as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "size,expect",
    [(MAX_BODY_BYTES, "passthrough"), (MAX_BODY_BYTES + 1, 413)],
)
async def test_exact_boundary(size: int, expect: str | int) -> None:
    filler = b" " * (size - 18) if size > 18 else b""
    payload = b'{"role":"student"}' + filler
    async with _client() as client:
        resp = await client.post(
            "/api/v1/auth/register",
            content=payload,
            headers={"content-type": "application/json"},
        )
    if expect == 413:
        assert resp.status_code == 413
    else:
        assert resp.status_code != 413  # 恰好 1MB 不触发限制
