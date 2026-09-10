# ADR-002: 限界上下文纵切物理分包，替代横切四层

- 状态：已接受
- 日期：2026-09-07
- 关联阶段：阶段 0（工程重启）

## 背景

传统做法是横切四层顶层分包：`app/domain`、`app/application`、`app/infrastructure`、`app/interfaces`。该结构下，同一子域的业务代码被拆散到四个顶层目录，限界上下文之间的边界只能靠命名约定和纪律维持；随着子域增多，任何一处改动都要横跨四个目录，耦合风险持续累积。

本项目按 DDD 划分了 5 个子域：identity（身份）、qa（问答）、course（课程）、reputation（声誉）、discovery（发现），需要一个让边界"物理可见"的结构。

## 决策

**按限界上下文纵切分包**，每个上下文内部再分四层：

```
app/
├── contexts/
│   ├── identity/{domain, application, infrastructure, interfaces}/
│   ├── qa/{domain, application, infrastructure, interfaces}/
│   ├── course/{domain, application, infrastructure, interfaces}/
│   ├── reputation/{domain, application, infrastructure, interfaces}/
│   └── discovery/{domain, application, infrastructure, interfaces}/
├── shared/        # 技术内核：DeclarativeBase、engine/redis、HTTP 中间件（认证依赖归 identity 公开供给面，不入 shared）
└── config/        # Pydantic Settings
```

配套规则：

1. **domain 层零框架依赖** —— 不 import FastAPI / SQLAlchemy，纯 Python 表达聚合与业务规则
2. **跨上下文协作只走应用层** —— 不直连他域仓储；跨聚合编排在 UseCase 中完成，配合领域事件（如 `AnswerAccepted`）
3. **公共技术设施上收到 `shared/`**（Base、engine/redis、HTTP 中间件）；上下文的 domain/application 层禁止跨域 import 他上下文私有实现——**例外**：identity 的 interfaces/api 认证依赖（`get_current_user` / `require_roles`）为公开供给面，下游上下文可在自己的 interfaces 层消费（详见 context-map 边界规则 4）

## 后果

正面：

1. 上下文边界物理化 —— `git` 目录即边界，跨域 import 在 code review 中一眼可见
2. 单上下文可独立演进、独立测试；后续若需拆分服务，切口已就位
3. 新成员按子域阅读代码，认知负担从"全项目"降为"单上下文"

负面/代价：

1. 目录层级更深，新文件需要先定位所属上下文
2. 上下文归属需要决策（如 Tag 归 qa 的 TagCatalog 聚合），偶尔存在模糊地带 —— 以领域事件与术语表为准裁决
