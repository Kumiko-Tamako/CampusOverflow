"""请求体大小限制中间件：流式计数 + 缓存重放（修复暴力测试 E-06）。

设计（2026-09-09 与用户批准）：
- 包装 ASGI receive 边转发边累计字节数，已读 chunk 缓存在内存；
- 未超限 → 重放缓存 chunk 给下游（否则路由拿到空 body）；
- 超限 → 不调用下游 app，直接发 413 JSON（缓存最多 limit+1 chunk，内存有界）；
- 不依赖 Content-Length（chunked 分块传输同样被拦截）；
- 处理 http.disconnect：客户端中途断开时中止等待。
"""

from __future__ import annotations

from starlette.types import ASGIApp, Message, Receive, Scope, Send

MAX_BODY_BYTES = 1_048_576  # 1 MiB


class BodyLimitMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int = MAX_BODY_BYTES) -> None:
        self._app = app
        self._max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        buffered: list[Message] = []
        total = 0
        over_limit = False
        disconnected = False

        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                disconnected = True
                break
            body: bytes = message.get("body", b"")
            total += len(body)
            if total > self._max_bytes:
                over_limit = True
                break  # 停止读取：不再为超大 body 消耗内存
            buffered.append(message)
            if not message.get("more_body", False):
                break

        if disconnected:
            return

        if over_limit:
            await self._send_413(send)
            return

        async def replay_receive() -> Message:
            if buffered:
                return buffered.pop(0)
            return await receive()  # 断开等后续消息（如 http.disconnect）

        await self._app(scope, replay_receive, send)

    async def _send_413(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        detail = b'{"detail":"request body too large"}'
        await send({"type": "http.response.body", "body": detail})
