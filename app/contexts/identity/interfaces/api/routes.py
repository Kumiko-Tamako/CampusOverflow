from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.contexts.identity.application.commands import RegisterCommand
from app.contexts.identity.application.register_use_case import RegisterUseCase
from app.contexts.identity.domain.errors import (
    EmailAlreadyExistsError,
    IdentityAlreadyExistsError,
    IdentityDomainError,
)
from app.contexts.identity.infrastructure.password_hasher import BcryptPasswordHasher
from app.contexts.identity.infrastructure.repository import SqlAlchemyUserRepository
from app.contexts.identity.interfaces.api.schemas import RegisterRequest, RegisterResponse
from app.shared.engine import get_session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _build_use_case(session: AsyncSession) -> RegisterUseCase:
    """组装用例：仓储 + 哈希器依赖注入（后续迁入统一 DI 容器）。"""
    return RegisterUseCase(SqlAlchemyUserRepository(session), BcryptPasswordHasher())


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="注册（学生/教师分流）",
)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> RegisterResponse:
    use_case = _build_use_case(session)
    command = RegisterCommand(
        role=payload.role,
        email=payload.email,
        password=payload.password,
        student_id=payload.student_id,
        staff_id=payload.staff_id,
    )
    try:
        user = await use_case.execute(command)
    except (EmailAlreadyExistsError, IdentityAlreadyExistsError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IdentityDomainError as exc:  # 弱密码 / 缺身份 / 未知角色
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except ValueError as exc:  # 值对象格式校验（学号/工号/邮箱）
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return RegisterResponse(
        id=user.id,
        role=user.role,
        email=user.email.value,
        student_id=user.student_id.value if user.student_id is not None else None,
        staff_id=user.staff_id.value if user.staff_id is not None else None,
        created_at=user.created_at,
    )
