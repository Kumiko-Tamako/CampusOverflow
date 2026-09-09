class IdentityDomainError(Exception):
    """identity 上下文领域错误基类。"""


class WeakPasswordError(IdentityDomainError):
    """密码不满足强度要求（≥8 位且同时含字母和数字）。"""


class EmailAlreadyExistsError(IdentityDomainError):
    """邮箱已被占用。"""


class IdentityAlreadyExistsError(IdentityDomainError):
    """学号/工号已被占用。"""


class IdentityRequiredError(IdentityDomainError):
    """注册时缺少与角色匹配的校园身份（学号或工号）。"""


class UnknownRoleError(IdentityDomainError):
    """未知的注册角色。"""
