"""QuestionRepository 集成测试：真 PostgreSQL（docker compose up -d）。

questions.author_id 外键指向 users，故先经注册用例建作者。
"""

from __future__ import annotations

import uuid

import pytest

from app.contexts.identity.application.commands import RegisterCommand
from app.contexts.identity.application.register_use_case import RegisterUseCase
from app.contexts.identity.infrastructure.password_hasher import BcryptPasswordHasher
from app.contexts.identity.infrastructure.repository import SqlAlchemyUserRepository
from app.contexts.qa.application.ask_question_use_case import AskQuestionUseCase
from app.contexts.qa.application.commands import AskQuestionCommand
from app.contexts.qa.infrastructure.repository import SqlAlchemyQuestionRepository
from app.shared.engine import session_factory

pytestmark = pytest.mark.integration


async def _make_author() -> uuid.UUID:
    """注册一个学生用户并 commit，返回其 user.id（供 question.author_id 外键）。"""
    async with session_factory() as session:
        use_case = RegisterUseCase(SqlAlchemyUserRepository(session), BcryptPasswordHasher())
        user = await use_case.execute(
            RegisterCommand(
                role="student",
                email=f"{uuid.uuid4()}@stu.edu.cn",
                password="Passw0rd8",
                student_id=str(uuid.uuid4().int)[:10],
            )
        )
        await session.commit()
        return user.id


async def test_question_persists_and_roundtrips() -> None:
    author_id = await _make_author()
    async with session_factory() as session:
        use_case = AskQuestionUseCase(SqlAlchemyQuestionRepository(session))
        question = await use_case.execute(
            AskQuestionCommand(
                title="  仓储回读测试标题  ",
                body="仓储回读测试正文",
                author_id=author_id,
            )
        )
        await session.commit()

        repo = SqlAlchemyQuestionRepository(session)
        fetched = await repo.get_by_id(question.id)
        assert fetched is not None
        assert fetched.id == question.id
        assert fetched.title.value == "仓储回读测试标题"  # 落库即规范化后形态
        assert fetched.body.value == "仓储回读测试正文"
        assert fetched.author_id == author_id
        assert fetched.created_at.tzinfo is not None


async def test_get_by_id_missing_returns_none() -> None:
    async with session_factory() as session:
        repo = SqlAlchemyQuestionRepository(session)
        assert await repo.get_by_id(uuid.uuid4()) is None
