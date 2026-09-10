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
| 2.4 | 提问：Question 聚合 + `POST /api/v1/questions` | 未开始（`feat/questions` 分支，PR #3） |
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

## 相关决策

- [ADR-001 采用 PostgreSQL 16 替代课程默认 MySQL 8](adr/ADR-001-postgresql.md)
- [ADR-002 限界上下文纵切物理分包](adr/ADR-002-context-partition.md)
