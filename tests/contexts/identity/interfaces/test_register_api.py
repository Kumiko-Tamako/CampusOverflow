"""注册接口集成测试：TestClient 打真接口 + 真 PostgreSQL。"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

pytestmark = pytest.mark.integration


def _payload() -> dict[str, str]:
    return {
        "role": "student",
        "email": f"{uuid.uuid4()}@stu.edu.cn",
        "password": "Passw0rd8",
        "student_id": str(uuid.uuid4().int)[:10],
    }


def test_register_returns_201_without_password() -> None:
    with TestClient(create_app()) as client:
        resp = client.post("/api/v1/auth/register", json=_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "student"
    assert body["email"].endswith("@stu.edu.cn")
    assert "password" not in body and "password_hash" not in body  # 响应不含密码


def test_register_duplicate_email_returns_409() -> None:
    payload = _payload()
    with TestClient(create_app()) as client:
        first = client.post("/api/v1/auth/register", json=payload)
        second = client.post(
            "/api/v1/auth/register",
            json={**payload, "student_id": str(uuid.uuid4().int)[:10]},
        )
    assert first.status_code == 201
    assert second.status_code == 409
    assert "邮箱" in second.json()["detail"]


def test_register_weak_password_returns_422() -> None:
    with TestClient(create_app()) as client:
        resp = client.post(
            "/api/v1/auth/register",
            json={**_payload(), "password": "abc123"},
        )
    assert resp.status_code == 422


def test_register_student_without_student_id_returns_422() -> None:
    payload = _payload()
    del payload["student_id"]
    with TestClient(create_app()) as client:
        resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


def test_register_bad_student_id_format_returns_422() -> None:
    with TestClient(create_app()) as client:
        resp = client.post(
            "/api/v1/auth/register",
            json={**_payload(), "student_id": "not-numeric!!!"},
        )
    assert resp.status_code == 422


def test_register_small_body_still_reaches_handler_after_body_limit() -> None:
    """中间件缓存+重放验证：1MB 内的 body 完整到达路由，注册成功。"""
    with TestClient(create_app()) as client:
        resp = client.post("/api/v1/auth/register", json=_payload())
    assert resp.status_code == 201
