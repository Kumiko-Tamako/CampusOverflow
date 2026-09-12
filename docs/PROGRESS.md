# CampusOverflow 进度表

> 里程碑状态对照，随开发推进更新。

## 里程碑总览

| 阶段 | 周次 | 主题 | 状态 | 关键验收 |
|:---|:---|:---|:---|:---|
| 阶段 0 | W1–W2 | 工程重启 | **完成** | 本地门禁全绿；GitHub Actions 变绿 |
| 阶段 1 | W3–W5 | Sprint 1 文档 | 进行中（1.1–1.4 产出完成） | 覆盖 Lab 2+3 全部提交物 |
| 阶段 2 | W7–W9 | Walking Skeleton | **进行中**（2.1–2.3 完成，PR #1/#2 已 merge） | 注册→登录已贯通；提问→列表→详情待开发；覆盖率 ≥70% |
| 阶段 3 | W11–W13 | 核心特性 | 未开始 | 覆盖率 70%+；契约测试；4 次 PR 评审记录 |
| 阶段 4 | W15 | 上线 | 未开始 | 线上 URL 可访问；Lab 8 提交物齐备 |

## 阶段 0 明细

| 步骤 | 内容 | 状态 |
|:---|:---|:---|
| 0.1 | 重写 README.md（定位 / 技术栈 / 架构决策） | 完成 |
| 0.2 | 工具链配置（requirements / pyproject / .gitignore），venv 装平 | 完成 |
| 0.3 | DDD 目录骨架（5 上下文 × 4 层 + shared + config） | 完成 |
| 0.4 | 最小可运行应用（settings / Base / create_app + /health） | 完成 |
| 0.5 | 冒烟测试 tests/test_health.py | 完成 |
| 0.6 | CI 工作流（ruff + mypy + pytest，无 services） | 完成 |
| 0.7 | Docker Compose（db + redis，双 healthcheck） | 完成 |
| 0.8 | 门禁全绿 + 首次提交 + CI 变绿 | 完成 |
| 0.9 | 项目文档（PROGRESS + ADR-001/002） | 完成 |

## 阶段 1 明细

| 步骤 | 内容 | 状态 |
|:---|:---|:---|
| 1.1 | docs/sprint/story-map.md（6 主干/11 活动/27 故事 + WS 切片） | 完成 |
| 1.2 | docs/sprint/product-backlog.md（27 故事 / 72 SP / INVEST + 价值成本矩阵） | 完成 |
| 1.3 | docs/sprint/acceptance-criteria.feature（11 功能域 / 34 场景，Lab 6 全覆盖） | 完成 |
| 1.4 | docs/domain/context-map.md / aggregates.md / glossary.md（46 术语 / 6 聚合） | 完成（待检测复核） |

## 阶段 2 明细（Walking Skeleton）

| 步骤 | 内容 | 状态 |
|:---|:---|:---|
| 2.1 | 注册：User 聚合 + `POST /api/v1/auth/register`（bcrypt 哈希 + 1MiB 请求体上限中间件） | **完成**（PR #1 已 merge；台账 `docs/test/2.1-register.md`，44 测试全绿） |
| 2.2 | 登录：`POST /api/v1/auth/login`，JWT Access 15min + Refresh 7d 存 Redis（GETDEL 原子轮换、可吊销） | **完成**（PR #2 已 merge） |
| 2.3 | 认证依赖：`get_current_user` + `require_roles` RBAC（`GET /api/v1/auth/me` 受保护示例） | **完成**（随 2.2 一并交付；台账 `docs/test/2.2-login.md`，67 测试全绿） |
| 2.4 | 提问：Question 聚合 + `POST /api/v1/questions` | **完成**（`feat/questions` 分支待提 PR #3；台账 `docs/test/2.4-question.md`，132 测试全绿，暴力测试前三路 15/15 + 第四路 20/20 PASS，第四路发现的 3 类 500 缺陷已修复） |
| 2.5 | 列表：`GET /api/v1/questions`（分页，默认按最新排序；投票排序迭代 2 再做） | 未开始（`feat/listing` 分支，PR #4） |
| 2.6 | 详情：`GET /api/v1/questions/{id}`（标签/答案区迭代 1 恒为空列表，404 不泄露信息） | 未开始（`feat/listing` 分支，PR #4） |
| 2.7 | 迁移纪律：`alembic revision --autogenerate` → 人工审核脚本才 `upgrade` | 2.1 已执行一次（`ab3c0dd6dd38`，含 roles 种子） |
| 2.8 | 契约交付：`openapi.json` 交前端队友 | 未开始 |

## 变更记录

> 纪律（2026-09-10 起）：AI 每次修改项目文件后同步登记本记录，写明改了哪些文件、什么内容。

| 日期 | 变更内容 |
|:---|:---|
| 2026-09-10 | `docs/test/2.2-login.md`：门禁拆分数字修正（46 单元/JWT + 19 集成 = 65；伪造令牌修复后 48+19=67）+ 修复后复测注记 |
| 2026-09-10 | `docs/PROGRESS.md`：阶段 2 标记进行中，新增阶段 2 明细表（2.1–2.8 状态）；同日增设本"变更记录"节 |
| 2026-09-10 | **2.4 开发前文档勘误**：[context-map.md](domain/context-map.md) 6 处（关系图 shared 框 + 图内箭头标签、图注①、关系#1/#5、边界规则 4 加"interfaces 层公开供给面"例外）——认证依赖（get_current_user/require_roles）归属从"shared 认证原语"勘正为"identity interfaces/api 公开供给面"；[ADR-002](adr/ADR-002-context-partition.md) 2 处（目录树注释、规则 3）、[glossary.md](domain/glossary.md) 1 处（术语 10"防腐层"）同步同一口径；仓库外 `暴力测试方案.md` 分页参数 `size`→`page_size`（S-04/S-05/S-08，S-05 补记上限 100） |
| 2026-09-10 | `docs/test/2.2-login.md`：删除第四节重复注记行（与修复后复测注记信息重复的 L47） |
| 2026-09-10 | **2.4 提问功能完成**（`feat/questions` 分支）：qa 上下文六步法——domain（Title/Body 值对象 + Question 聚合 + QuestionPublished + 仓储端口，不建 errors.py）、application（AskQuestionUseCase）、infra（questions 表迁移 `346e395dfea8`，author_id CASCADE+索引、created_at 索引）、interfaces（qa 路由 201/401/422/413；identity deps 纯增量导出 `CurrentUser` 公开供给面，qa 对 identity.domain 0 import）；新增 33 测试（总 **100 passed**）、ruff 0、mypy 57 文件 0；真实服务暴力测试 Q-01~Q-12 + 附加 3 项 **15/15 PASS**（Q-12 并发 50 帖全 201/ID 唯一）；台账 [2.4-question.md](test/2.4-question.md) |
| 2026-09-10 | **2.4 第四路暴力测试 3 类 500 缺陷修复**（P-01~P-04，系统性波及 register/login）：新增 `app/shared/text_validation.py`（拒 C0 控制字符（放行 `\t\n\r`）+ lone surrogate，纯标准库共享内核）、`app/shared/exception_handlers.py`（自定义 RequestValidationError 处理器只回 type/loc/msg 不回显 input，治 surrogate 编码崩溃/递归炸弹爆栈；SQLAlchemyError 统一 400 兜底）；`app/main.py` 挂载两处理器；qa Title/Body 与 identity Email/StudentId/StaffId 五个 VO `__post_init__` 接入字符校验；identity schemas 的 RegisterRequest/LoginRequest 加 field_validator（注册用例查重 SQL 先于 VO 构造，NUL 必须在 schema 边界拦；login identifier 直接进查询参数同理；不碰格式，SQL 注入串仍 401）；新增测试 32 条（`tests/test_text_validation.py` 14、`tests/test_validation_handlers.py` 5 进 CI，qa/identity VO 单测 8，questions 集成 4 + login SQLi 守护 1），总 **132 passed**（CI 同款 95 passed）、ruff 0、mypy 59 文件 0；真实服务 verify 8/8 复现点全转 422、`bruteforce_24_extra.py` **20/20 PASS**；台账 [2.4-question.md](test/2.4-question.md) 增第七节 |
| 2026-09-12 | `docs/test/2.4-question.md`：补充 5.4 第四路协议层缺陷修复记录、5.5 第五路 N 系列独立测试 **15/15 PASS**（emoji/零宽字符/码点边界/组合攻击/中间件优先级/重放/兼容性，2026-09-11 执行）、5.6 L-08 flaky 测试实证（JWT 签名末字符 1/64 概率空篡改，测试缺陷非产品缺陷，修法待批） |

## 相关决策

- [ADR-001 采用 PostgreSQL 16 替代课程默认 MySQL 8](adr/ADR-001-postgresql.md)
- [ADR-002 限界上下文纵切物理分包](adr/ADR-002-context-partition.md)
