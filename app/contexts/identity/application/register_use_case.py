from __future__ import annotations

from app.contexts.identity.application.commands import RegisterCommand
from app.contexts.identity.application.ports import PasswordHasher
from app.contexts.identity.domain.errors import (
    EmailAlreadyExistsError,
    IdentityAlreadyExistsError,
    IdentityRequiredError,
    UnknownRoleError,
)
from app.contexts.identity.domain.repository import UserRepository
from app.contexts.identity.domain.user import Role, User, validate_password_strength
from app.contexts.identity.domain.value_objects import StaffId, StudentId


class RegisterUseCase:
    """注册用例：学生/教师分流 + 唯一性校验 + 哈希落库（US-R01/R02/R03/R04）。"""

    def __init__(self, repository: UserRepository, hasher: PasswordHasher) -> None:
        self._repository = repository
        self._hasher = hasher

    async def execute(self, command: RegisterCommand) -> User:
        validate_password_strength(command.password)

        if await self._repository.get_by_email(command.email) is not None:
            raise EmailAlreadyExistsError(f"邮箱已被占用：{command.email}")

        role: Role
        identity_value: str
        if command.role == "student":
            if command.student_id is None:
                raise IdentityRequiredError("学生注册必须提供学号")
            if await self._repository.get_by_student_id(command.student_id) is not None:
                raise IdentityAlreadyExistsError(f"学号已被占用：{command.student_id}")
            _ = StudentId(command.student_id)  # 格式校验
            role, identity_value = "student", command.student_id
        elif command.role == "teacher":
            if command.staff_id is None:
                raise IdentityRequiredError("教师注册必须提供工号")
            if await self._repository.get_by_staff_id(command.staff_id) is not None:
                raise IdentityAlreadyExistsError(f"工号已被占用：{command.staff_id}")
            _ = StaffId(command.staff_id)  # 格式校验
            role, identity_value = "teacher", command.staff_id
        else:
            raise UnknownRoleError(f"未知角色：{command.role}")

        password_hash = await self._hasher.hash(command.password)
        user = User.register(
            role=role,
            email_value=command.email,
            password_hash_value=password_hash,
            identity_value=identity_value,
        )
        await self._repository.add(user)
        return user
