"""UserRepository 集成测试：需要本地 PostgreSQL（docker compose up -d）。"""

import uuid

import pytest

from app.contexts.identity.application.commands import RegisterCommand
from app.contexts.identity.application.register_use_case import RegisterUseCase
from app.contexts.identity.domain.errors import EmailAlreadyExistsError, IdentityAlreadyExistsError
from app.contexts.identity.infrastructure.password_hasher import BcryptPasswordHasher
from app.contexts.identity.infrastructure.repository import SqlAlchemyUserRepository
from app.shared.engine import session_factory

pytestmark = pytest.mark.integration


def _unique_email() -> str:
    return f"{uuid.uuid4()}@stu.edu.cn"


def _unique_student_id() -> str:
    return str(uuid.uuid4().int)[:10]


async def test_register_student_persists_and_roundtrips() -> None:
    email = _unique_email()
    student_id = _unique_student_id()
    async with session_factory() as session:
        use_case = RegisterUseCase(SqlAlchemyUserRepository(session), BcryptPasswordHasher())
        user = await use_case.execute(
            RegisterCommand(
                role="student", email=email, password="Passw0rd8", student_id=student_id
            )
        )
        await session.commit()

        repo = SqlAlchemyUserRepository(session)
        fetched = await repo.get_by_email(email)
        assert fetched is not None and fetched.id == user.id
        assert fetched.password_hash.value.startswith("$2b$")  # 库里是哈希非明文

        by_student = await repo.get_by_student_id(student_id)
        assert by_student is not None and by_student.id == user.id

        assert await repo.get_by_email(f"missing-{uuid.uuid4()}@stu.edu.cn") is None


async def test_duplicate_email_rejected_in_db() -> None:
    email = _unique_email()
    async with session_factory() as session:
        use_case = RegisterUseCase(SqlAlchemyUserRepository(session), BcryptPasswordHasher())
        await use_case.execute(
            RegisterCommand(
                role="student",
                email=email,
                password="Passw0rd8",
                student_id=_unique_student_id(),
            )
        )
        await session.commit()

    async with session_factory() as session:
        use_case = RegisterUseCase(SqlAlchemyUserRepository(session), BcryptPasswordHasher())
        with pytest.raises(EmailAlreadyExistsError):
            await use_case.execute(
                RegisterCommand(
                    role="student",
                    email=email,
                    password="Passw0rd8",
                    student_id=_unique_student_id(),
                )
            )


async def test_duplicate_student_id_rejected_in_db() -> None:
    student_id = _unique_student_id()
    async with session_factory() as session:
        use_case = RegisterUseCase(SqlAlchemyUserRepository(session), BcryptPasswordHasher())
        await use_case.execute(
            RegisterCommand(
                role="student",
                email=_unique_email(),
                password="Passw0rd8",
                student_id=student_id,
            )
        )
        await session.commit()

    async with session_factory() as session:
        use_case = RegisterUseCase(SqlAlchemyUserRepository(session), BcryptPasswordHasher())
        with pytest.raises(IdentityAlreadyExistsError):
            await use_case.execute(
                RegisterCommand(
                    role="student",
                    email=_unique_email(),
                    password="Passw0rd8",
                    student_id=student_id,
                )
            )


async def test_register_teacher_persists() -> None:
    email = _unique_email()
    staff_id = f"T{uuid.uuid4().int % 10_000 + 1_000}"
    async with session_factory() as session:
        use_case = RegisterUseCase(SqlAlchemyUserRepository(session), BcryptPasswordHasher())
        user = await use_case.execute(
            RegisterCommand(role="teacher", email=email, password="Passw0rd8", staff_id=staff_id)
        )
        await session.commit()

        repo = SqlAlchemyUserRepository(session)
        fetched = await repo.get_by_staff_id(staff_id)
        assert fetched is not None and fetched.id == user.id
        assert fetched.role == "teacher"
