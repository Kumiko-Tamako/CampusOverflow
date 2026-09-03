# CampusOverflow 🎓 项目目前设计

> 校园问答知识社区 —— 沉淀教学答疑，量化学习参与

CampusOverflow 是一个面向高校场景的问答知识社区平台。学生可以按课程、教师、班级组织知识讨论；教师可以将答疑工作沉淀为可复用的教学资产；学院可以量化学生学习参与度作为过程评价依据。

---

## 技术栈

| 层次 | 技术选型 | 选型理由 |
|:---|:---|:---|
| **编程语言** | Python 3.12+ | 类型注解全项目覆盖 + mypy strict 门禁，对标 TS 严格模式；语法简洁，开发效率高 |
| **Web 框架** | FastAPI 0.115+ + Uvicorn | 原生异步；自动生成 OpenAPI 3.1 文档，契约优先开发天然落地；内置依赖注入 |
| **持久化** | SQLAlchemy 2.0（异步）+ Alembic + PostgreSQL 16 | 声明式 ORM 映射，为 DDD 战术建模提供落地媒介；Alembic 版本化迁移对标 Flyway |
| **数据校验** | Pydantic v2 | FastAPI 原生集成，Rust 内核性能极高；统一 Request/Response Schema |
| **缓存** | Redis 7 | 会话存储、热点问题缓存、限流计数器、Celery 消息队列 |
| **API 风格** | RESTful + OpenAPI 3（自动生成） | FastAPI 自动产出 openapi.json，契约驱动前后端并行开发 |
| **异步任务** | Celery + Redis Broker | 声誉计算、通知推送、邮件发送、定时排行榜更新 |
| **搜索** | PostgreSQL 全文检索（MVP）→ Elasticsearch 8（演进） | MVP 阶段零额外依赖，后续按需升级 |
| **对象存储** | MinIO（S3 兼容） | 用户头像、图片附件存储；可平滑迁移到阿里云 OSS |
| **测试** | pytest 8 + httpx + Testcontainers + pytest-cov | 覆盖测试金字塔三层；Testcontainers 启动真实容器做集成测试 |
| **代码质量** | ruff + mypy --strict + pre-commit | ruff 统一 lint/format 对标 ESLint+Prettier；mypy strict 对标 tsc 严格模式 |
| **静态分析** | SonarQube + coverage.py | 持续质量检测、技术债度量、覆盖率门禁 |
| **日志** | Loguru（JSON 结构化日志） | 对标 Logback 的结构化日志输出 |
| **可观测性** | Prometheus + Grafana + prometheus-fastapi-instrumentator | HTTP 指标、业务 KPI 曲线、告警规则 |
| **版本控制** | Git + GitHub / Gitee | Pull Request 流程训练代码评审能力 |
| **CI/CD** | GitHub Actions + Docker | 完整 DevOps 流水线：lint → typecheck → test → build → deploy |
| **部署** | Docker Compose + Nginx | 一键启动整套环境；为后续 Kubernetes 预留接口 |
| **前端框架** | React 18 + TypeScript 5 | 行业主流；TS 强制类型，贴合工程教学；函数式 + Hooks 与现代生态对齐 |
| **前端工具链** | Vite + ESLint + Prettier | 开箱即用的现代开发体验，毫秒级 HMR；统一代码风格门禁 |
| **前端状态管理** | Zustand + TanStack Query | 避免 Redux 模板代码；服务器状态与客户端状态分离的最佳实践 |
| **前端 UI** | Ant Design 5 / Tailwind CSS | 企业级组件库，降低 UI 实现成本；Tailwind 用于定制化 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React 18 + TS 5)           │
│    Vite · Ant Design 5 · Zustand · TanStack Query       │
│              ESLint · Prettier · Husky                   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / REST + OpenAPI 契约
                       ▼
┌─────────────────────────────────────────────────────────┐
│               API Gateway (Nginx)                        │
│         /api → FastAPI · / → SPA 静态资源                │
└──────────────────────┬──────────────────────────────────┘
                       │
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Interfaces  │  │ Application │  │   Domain    │     │
│  │  (API/路由)  │──│  (用例编排)  │──│  (实体/规则) │     │
│  └─────────────┘  └─────────────┘  └──────┬──────┘     │
│                                           │            │
│  ┌────────────────────────────────────────┘            │
│  │  Infrastructure                                     │
│  │  SQLAlchemy · Redis · MinIO · Celery · Loguru       │
│  └─────────────────────────────────────────────────────┘
└──────┬──────────────────────┬──────────────────┬───────┘
       │                      │                  │
       ▼                      ▼                  ▼
┌──────────┐          ┌──────────┐        ┌──────────┐
│PostgreSQL│          │  Redis   │        │  MinIO   │
│   16     │          │    7     │        │  对象存储  │
└──────────┘          └──────────┘        └──────────┘
```

### 架构设计原则

- **六边形架构** — 领域层零外部依赖，通过端口与适配器模式隔离基础设施
- **DDD 战术建模** — 实体、值对象、聚合、仓储、领域事件分层清晰
- **依赖倒置** — 领域层定义接口，基础设施层实现，通过依赖注入组装
- **契约优先** — FastAPI 自动生成 OpenAPI 规范，前后端基于契约并行开发

---

## 项目结构

```
campus-overflow/
├── app/
│   ├── domain/              # 领域层
│   │   ├── entities/        # 实体（Question, User, Answer, Vote）
│   │   ├── value_objects/   # 值对象（Tag, ReputationScore, CourseId）
│   │   ├── aggregates/      # 聚合根
│   │   ├── events/          # 领域事件
│   │   └── repositories/    # 仓储接口（抽象类/Protocol）
│   ├── application/         # 应用层
│   │   ├── use_cases/       # 用例（提问、回答、投票、悬赏）
│   │   ├── dtos/            # 数据传输对象
│   │   └── interfaces/      # 应用服务接口
│   ├── infrastructure/      # 基础设施层
│   │   ├── persistence/     # SQLAlchemy 实体映射 + Repository 实现
│   │   ├── cache/           # Redis 缓存实现
│   │   ├── event_bus/       # 事件总线实现
│   │   └── external/        # 外部服务（邮件、OAuth）
│   ├── interfaces/          # 接口层（FastAPI）
│   │   ├── api/v1/          # 路由模块（按子域拆分）
│   │   │   ├── questions.py
│   │   │   ├── answers.py
│   │   │   ├── users.py
│   │   │   ├── courses.py
│   │   │   └── tags.py
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   └── deps.py          # 依赖注入容器
│   ├── config/              # 配置管理（Pydantic Settings）
│   └── main.py              # FastAPI 应用入口
├── tests/
│   ├── unit/                # 纯领域逻辑测试（无需基础设施）
│   ├── integration/         # Testcontainers 集成测试
│   └── e2e/                 # 端到端测试
├── deploy/                  # 部署配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx/
├── alembic/                 # 数据库迁移脚本
├── pyproject.toml           # 统一依赖 + 工具配置
├── .github/workflows/       # CI/CD 流水线
├── .pre-commit-config.yaml
└── README.md
```

---

## 业务子域

| 子域 | 核心实体 | 说明 |
|:---|:---|:---|
| **身份与认证** | User, Role, Student, Teacher | 学号/工号登录、RBAC 权限、校园身份认证 |
| **问答核心** | Question, Answer, Comment, Vote, Tag | 提问/回答/投票/评论，按课程/标签组织 |
| **课程与班级** | Course, ClassGroup, Enrollment | 课程关联、班级圈、师生认证 |
| **声誉与激励** | Reputation, Badge, Bounty, Leaderboard | 声誉值、徽章、悬赏积分、学风画像 |
| **内容发现** | Search, Trending, Recommendation | 全文搜索、热门推荐、通知中心 |

---

## 快速开始

### 前置要求

- Python 3.12+
- Docker & Docker Compose
- Node.js 18+（前端开发）

### 启动后端

```bash
# 克隆仓库
git clone https://github.com/your-org/campus-overflow.git
cd campus-overflow

# 安装依赖
pip install -e ".[dev]"

# 启动基础设施（PostgreSQL + Redis + MinIO）
docker compose up -d postgres redis minio

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173` 浏览前端，`http://localhost:8000/docs` 查看 API 文档。

---

## 课程对标

本项目配套《软件工程》课程，各阶段对应关系：

| 课程阶段 | 对应内容 | 关键交付物 |
|:---|:---|:---|
| Lab 1-2 | 团队组建、需求分析、用户故事 | 用户故事地图、Backlog |
| Lab 3-4 | DDD 事件风暴、领域建模 | 领域模型图、六边形架构骨架 |
| Lab 5 | 前后端框架搭建、CI 配置 | 可运行原型、CI 流水线 |
| Lab 6 | 核心业务功能实现 | 问答、投票、声誉功能 |
| Lab 7 | 测试与质量保障 | 单元/集成测试、SonarQube |
| Lab 8 | 部署与持续交付 | Docker Compose 部署、CD 流水线 |

---

## License

MIT
