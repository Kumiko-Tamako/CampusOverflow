# CampusOverflow 项目目标与总体设计

> 校园问答知识社区 —— 沉淀教学答疑、量化学习参与

## 一、项目总目标

用 Python/FastAPI 技术栈、按 DDD 限界上下文纵切的单体架构，在 4 个 Sprint 内自主交付通过 CS-SE-301《软件工程》全部 8 个 Lab 考核点的 CampusOverflow 校园问答平台。全程不参考、不复制任何开源项目代码，方法论仅来自课程理论课。

终态三条硬指标：

1. **CI 全绿** —— ruff + mypy --strict + pytest 三项门禁全部通过
2. **系统上线可访问** —— Docker Compose 部署，线上 URL 可用
3. **监控可观测** —— Prometheus + Grafana 核心指标与告警就位

## 二、里程碑规划

| 阶段 | 周次 | 主题 | 关键交付物 | 验收标准 |
|:---|:---|:---|:---|:---|
| 阶段 0 | W1–W2 | 工程重启 | README、工具链配置、目录骨架、最小应用 + /health、冒烟测试、CI、Compose、项目文档 | 本地门禁全绿；GitHub Actions 变绿 |
| 阶段 1 | W3–W5 | Sprint 1 文档 | 用户故事地图、Product Backlog、Gherkin 验收标准（≥8 条）、限界上下文图 / 聚合清单 / 术语表（≥30 条） | 覆盖 Lab 2+3 全部提交物与评分点 |
| 阶段 2 | W7–W9 | Walking Skeleton | 注册 → 登录 → 提问 → 列表 → 详情 端到端纵切贯通（每功能走六步法） | 端到端贯通；覆盖率 ≥70%；openapi.json 交付前端 |
| 阶段 3 | W11–W13 | 核心特性 | 回答、投票、采纳（领域事件）、评论、标签、声誉（Celery）；测试冲刺 | 覆盖率 70%+（核心聚合 90%+）；契约测试 1 条；4 次 PR 评审记录 |
| 阶段 4 | W15 | 上线 | 多阶段 Dockerfile、生产编排、CI/CD 扩展、Prometheus + Grafana、运维手册 | 线上 URL 可访问；Lab 8 提交物齐备 |

## 三、技术栈

| 层次 | 选型 | 选型理由 |
|:---|:---|:---|
| **编程语言** | Python 3.12+ | 类型注解全项目覆盖 + mypy --strict 门禁；语法简洁，异步生态成熟 |
| **Web 框架** | FastAPI + Uvicorn | 原生异步；自动生成 OpenAPI 3.1，契约优先天然落地；内置依赖注入 |
| **ORM / 迁移** | SQLAlchemy 2.0（async）+ Alembic | 声明式映射承载 DDD 战术建模；Alembic 版本化迁移 |
| **数据库** | PostgreSQL 16 | JSONB、全文检索能力，asyncpg 异步驱动生态完整 |
| **缓存 / Broker** | Redis 7 | Refresh Token 存储（可吊销）、热点缓存、限流计数、Celery Broker |
| **数据校验** | Pydantic v2 | FastAPI 原生集成；统一 Request/Response Schema |
| **异步任务** | Celery | 声誉流水、通知推送等异步化，接口响应不受拖累 |
| **测试** | pytest + pytest-asyncio + httpx | 覆盖测试金字塔；异步友好 |
| **代码质量** | ruff + mypy --strict | lint / format 统一；严格类型门禁 |
| **CI/CD** | GitHub Actions | lint → typecheck → test → build → deploy 全流水线 |
| **部署** | Docker Compose + Nginx | 一键起环境；生产编排与监控同栈 |
| **前端** | React 18 + TypeScript 5 | 契约驱动前后端并行开发 |

## 四、架构决策

```
                 ┌──────────────────────────────────┐
                 │      Frontend (React 18 + TS 5)  │
                 └────────────────┬─────────────────┘
                                  │ REST / OpenAPI 3.1 契约
                                  ▼
┌──────────────── FastAPI 单体（限界上下文纵切，模块化分包）────────────────┐
│                                                                          │
│   identity          qa            course        reputation    discovery  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ ┌────────┐│
│  │ interfaces │  │ interfaces │  │ interfaces │  │interfaces│ │interfaces│
│  │ application│  │ application│  │ application│  │application│ │application│
│  │    infra   │  │    infra   │  │    infra   │  │   infra  │ │  infra  ││
│  │   domain   │  │   domain   │  │   domain   │  │  domain  │ │ domain  ││
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ └────────┘│
│               shared（通用内核：Base、事件、认证原语）· config            │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   ▼
        PostgreSQL 16            Redis 7            Celery Worker
```

### 设计原则

- **限界上下文纵切** —— 按子域物理分包替代横切四层，上下文即演进边界
- **DDD 战术建模** —— 实体 / 值对象 / 聚合 / 领域事件 / 仓储端口分层清晰
- **依赖倒置** —— domain 层不 import FastAPI / SQLAlchemy，基础设施层实现端口，依赖注入组装
- **聚合刻意收小** —— 如 Question 聚合仅含 Question + Vote；跨聚合协作走应用层编排 + 领域事件
- **契约优先** —— openapi.json 先行交付前端，mock 并行、互不阻塞

### 关键技术决策

| 主题 | 决策 |
|:---|:---|
| 认证 | JWT：Access 15min + Refresh 7d 存 Redis（可吊销）；RBAC 角色权限 |
| 密码存储 | bcrypt 哈希 |
| 标签 | Tag 值对象，归属 TagCatalog 聚合 |
| 主键 | UUID |
| 声誉 | reputation_ledgers 流水表，event_id 唯一索引保证幂等 |

## 五、业务子域

| 限界上下文 | 核心聚合 / 对象 | 职责 |
|:---|:---|:---|
| **identity** | User、StudentId / Email 值对象、RBAC | 注册登录、学生/教师分流、认证授权 |
| **qa** | Question（+Vote）、Answer（+Vote+Comment）、TagCatalog | 提问 / 回答 / 投票 / 评论 / 采纳 / 标签 |
| **course** | Course、Enrollment | 课程关联、班级组织 |
| **reputation** | ReputationLedger | 声誉流水、量化学习参与度 |
| **discovery** | Search、Trending | 检索与热门发现 |

## 六、课程考核对照

| Lab | 对应阶段 | 提交物 |
|:---|:---|:---|
| Lab 2 | 阶段 1 | 用户故事地图、Product Backlog（逐条过 INVEST） |
| Lab 3 | 阶段 1 | Gherkin 验收标准、事件风暴产出（上下文图 / 聚合清单 / 术语表） |
| Lab 4 | 阶段 2 | Walking Skeleton、版本化迁移、六步法记录 |
| Lab 5 | 阶段 2 | 前后端契约（openapi.json）、CI 流水线 |
| Lab 6 | 阶段 3 | 回答 / 投票 / 采纳 / 标签 / 声誉功能 |
| Lab 7 | 阶段 3 | 覆盖率报告、契约测试、PR 评审记录 |
| Lab 8 | 阶段 4 | 上线 URL、CD 流水线、监控 Dashboard、运维手册 |

Lab 1（团队组建）为课程环节，不涉及代码交付。

## 七、质量门禁

- pytest 全绿；`ruff check .` 零告警；`mypy app` --strict 零错误
- 覆盖率：整体 ≥70%，核心聚合 ≥90%
- 迁移纪律：`alembic revision --autogenerate` 生成后人工审核才应用
- CI：GitHub Actions 三项门禁全绿才算通过
