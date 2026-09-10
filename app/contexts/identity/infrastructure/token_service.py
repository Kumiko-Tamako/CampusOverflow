from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from jose import JWTError, jwt

from app.contexts.identity.application.ports import ACCESS_TOKEN_TTL, REFRESH_TOKEN_TTL
from app.contexts.identity.domain.user import User


class JwtTokenService:
    """TokenService 端口的 python-jose 实现（HS256）。

    - Access 令牌：typ=access，TTL 15min
    - Refresh 令牌：typ=refresh + jti，TTL 7d（jti 用于 Redis 存储与原子消耗）
    - decode 钉死 algorithms=["HS256"]，拒绝 alg:none 等降级攻击
    """

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def issue_access(self, user: User) -> str:
        return self._encode(user_id=user.id, typ="access", ttl=ACCESS_TOKEN_TTL)

    def issue_refresh(self, user: User) -> tuple[str, UUID]:
        jti = uuid4()
        return self._encode(user_id=user.id, typ="refresh", ttl=REFRESH_TOKEN_TTL, jti=jti), jti

    def verify_access(self, token: str) -> UUID | None:
        payload = self._decode(token)
        if payload is None or payload.get("typ") != "access":
            return None
        sub = payload.get("sub")
        if not isinstance(sub, str):
            return None
        try:
            return UUID(sub)
        except ValueError:
            # 签名合法但 sub 非 UUID 格式（伪造令牌）→ 按无效处理，不抛 500
            return None

    def decode_refresh(self, token: str) -> tuple[UUID, UUID] | None:
        payload = self._decode(token)
        if payload is None or payload.get("typ") != "refresh":
            return None
        sub = payload.get("sub")
        jti = payload.get("jti")
        if not isinstance(sub, str) or not isinstance(jti, str):
            return None
        try:
            return UUID(sub), UUID(jti)
        except ValueError:
            # 签名合法但 sub/jti 非 UUID 格式（伪造令牌）→ 按无效处理，不抛 500
            return None

    def _encode(
        self,
        *,
        user_id: UUID,
        typ: str,
        ttl: timedelta,
        jti: UUID | None = None,
    ) -> str:
        now = datetime.now(UTC)
        claims: dict[str, object] = {
            "sub": str(user_id),
            "typ": typ,
            "iat": now,
            "exp": now + ttl,
        }
        if jti is not None:
            claims["jti"] = str(jti)
        return jwt.encode(claims, self._secret, algorithm="HS256")

    def _decode(self, token: str) -> dict[str, object] | None:
        try:
            return jwt.decode(token, self._secret, algorithms=["HS256"])
        except JWTError:
            return None
