"""提问接口集成测试：httpx ASGI 传输 + 真 PostgreSQL + 真 Redis（登录写 refresh）。

覆盖：201 正常发布（含 strip 端到端）/ 401 未认证 / 422 校验族 / 413 超大 body。
"""

from __future__ import annotations

import uuid
from typing import Any

import httpx
import pytest

from app.main import create_app

pytestmark = pytest.mark.integration

BASE_URL = "http://test"


@pytest.fixture
async def client(redis_cleanup: None) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as c:
        yield c


async def _register_and_login(client: httpx.AsyncClient) -> tuple[str, str]:
    """注册并登录，返回 (access_token, user_id)。"""
    payload = {
        "role": "student",
        "email": f"{uuid.uuid4()}@stu.edu.cn",
        "password": "Passw0rd8",
        "student_id": str(uuid.uuid4().int)[:10],
    }
    reg = await client.post("/api/v1/auth/register", json=payload)
    assert reg.status_code == 201, reg.text
    login = await client.post(
        "/api/v1/auth/login",
        json={"identifier": payload["student_id"], "password": payload["password"]},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    return token, me.json()["id"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _question_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": "如何理解数据库第三范式？",
        "body": "教材看不太懂，求举例说明。",
    }
    payload.update(overrides)
    return payload


def _assert_no_input_echo(resp: httpx.Response) -> None:
    """422 不得回显攻击者原始输入：列表形态错误项只许有 type/loc/msg；
    字符串形态（路由捕获 ValueError）时，原始字节中也不许出现 NUL/代理转义。"""
    detail = resp.json()["detail"]
    if isinstance(detail, list):
        for item in detail:
            assert set(item.keys()) == {"type", "loc", "msg"}
    assert b"\x00" not in resp.content and b"\\u0000" not in resp.content
    assert b"\\ud800" not in resp.content


async def test_ask_question_returns_201(client: httpx.AsyncClient) -> None:
    token, user_id = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions", json=_question_payload(), headers=_auth(token)
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    # 白名单字段恰好 5 个，无任何内部字段
    assert set(body.keys()) == {"id", "title", "body", "author_id", "created_at"}
    assert body["author_id"] == user_id  # 作者取自令牌，非请求体
    assert body["title"] == "如何理解数据库第三范式？"
    uuid.UUID(body["id"])  # id 为合法 UUID


async def test_title_with_surrounding_spaces_is_stripped(client: httpx.AsyncClient) -> None:
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions",
        json=_question_payload(title="  带空格的标题  "),
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["title"] == "带空格的标题"


async def test_ask_without_token_returns_401(client: httpx.AsyncClient) -> None:
    resp = await client.post("/api/v1/questions", json=_question_payload())
    assert resp.status_code == 401


async def test_ask_with_bad_token_returns_401(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/questions", json=_question_payload(), headers=_auth("garbage.token")
    )
    assert resp.status_code == 401


async def test_empty_title_returns_422(client: httpx.AsyncClient) -> None:
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions", json=_question_payload(title=""), headers=_auth(token)
    )
    assert resp.status_code == 422


async def test_blank_title_returns_422(client: httpx.AsyncClient) -> None:
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions", json=_question_payload(title="    "), headers=_auth(token)
    )
    assert resp.status_code == 422


async def test_title_too_long_returns_422(client: httpx.AsyncClient) -> None:
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions",
        json=_question_payload(title="a" * 101),
        headers=_auth(token),
    )
    assert resp.status_code == 422


async def test_body_too_long_returns_422(client: httpx.AsyncClient) -> None:
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions",
        json=_question_payload(body="x" * 5001),
        headers=_auth(token),
    )
    assert resp.status_code == 422


async def test_missing_body_returns_422(client: httpx.AsyncClient) -> None:
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions", json={"title": "只有标题"}, headers=_auth(token)
    )
    assert resp.status_code == 422


async def test_extra_field_returns_422(client: httpx.AsyncClient) -> None:
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions",
        json=_question_payload(hacker=1),
        headers=_auth(token),
    )
    assert resp.status_code == 422


async def test_oversized_body_returns_413(client: httpx.AsyncClient) -> None:
    # body_limit 中间件在路由/鉴权之外层：超限直接 413，不进 schema 校验
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions",
        json=_question_payload(body="a" * (1024 * 1024 + 100)),
        headers=_auth(token),
    )
    assert resp.status_code == 413


async def test_nul_in_title_returns_422(client: httpx.AsyncClient) -> None:
    # P-01：NUL 无法存入 PostgreSQL，值对象在落库前拦截（旧行为 500）
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions",
        json=_question_payload(title="a\x00b 攻击"),
        headers=_auth(token),
    )
    assert resp.status_code == 422
    _assert_no_input_echo(resp)


async def test_nul_in_body_returns_422(client: httpx.AsyncClient) -> None:
    # P-02：正文 NUL 同样 422
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions",
        json=_question_payload(body="x\x00y"),
        headers=_auth(token),
    )
    assert resp.status_code == 422
    _assert_no_input_echo(resp)


async def test_lone_surrogate_title_returns_422(client: httpx.AsyncClient) -> None:
    # P-03：lone surrogate 被 Pydantic 拦截；422 处理器不回显 input，
    # 避免响应体 UTF-8 编码崩溃（旧行为 UnicodeEncodeError → 500）
    token, _ = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/questions",
        content=b'{"title":"\\ud800\\ud800","body":"ok"}',
        headers={**_auth(token), "content-type": "application/json"},
    )
    assert resp.status_code == 422
    _assert_no_input_echo(resp)


async def test_recursive_bomb_returns_422(client: httpx.AsyncClient) -> None:
    # P-04：depth=2000 的 JSON（12KB，绕过 1MB body 上限）；422 处理器不递归
    # 遍历回显 input，避免 jsonable_encoder 爆栈（旧行为 RecursionError → 500）
    token, _ = await _register_and_login(client)
    bomb = b'{"a":' * 2000 + b"1" + b"}" * 2000
    resp = await client.post(
        "/api/v1/questions",
        content=bomb,
        headers={**_auth(token), "content-type": "application/json"},
    )
    assert resp.status_code == 422
    _assert_no_input_echo(resp)
