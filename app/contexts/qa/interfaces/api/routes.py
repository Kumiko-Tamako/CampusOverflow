from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.contexts.identity.interfaces.api.deps import CurrentUser
from app.contexts.qa.application.ask_question_use_case import AskQuestionUseCase
from app.contexts.qa.application.commands import AskQuestionCommand
from app.contexts.qa.infrastructure.repository import SqlAlchemyQuestionRepository
from app.contexts.qa.interfaces.api.schemas import AskQuestionRequest, QuestionResponse
from app.shared.engine import get_session

router = APIRouter(prefix="/api/v1/questions", tags=["questions"])


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="发布问题（登录用户）",
)
async def ask_question(
    payload: AskQuestionRequest,
    user: CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> QuestionResponse:
    use_case = AskQuestionUseCase(SqlAlchemyQuestionRepository(session))
    try:
        question = await use_case.execute(
            AskQuestionCommand(
                title=payload.title,
                body=payload.body,
                author_id=user.id,  # 作者只取令牌中的当前用户，绝不取自请求体
            )
        )
    except ValueError as exc:  # Title/Body 值对象兜底校验（schema 已拦大部分形态）
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return QuestionResponse(
        id=question.id,
        title=question.title.value,
        body=question.body.value,
        author_id=question.author_id,
        created_at=question.created_at,
    )
