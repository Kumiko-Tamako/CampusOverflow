# Sprint 1 · 限界上下文图（Context Map）

> 事件风暴产出（Lab 3 评分点：上下文划分合理性）。
> 划分依据：`GOALS.md` 业务子域 + `story-map.md` 6 主干；物理分包策略见 `docs/adr/ADR-002-context-partition.md`。

## 一、上下文总览

| 上下文 | 类型 | 职责 | 包含聚合 | 对应故事主干 |
|:---|:---|:---|:---|:---|
| **identity** | 核心域 | 注册登录、校园身份、RBAC 认证授权 | User | E1 注册与身份 |
| **qa** | 核心域 | 提问 / 回答 / 投票 / 评论 / 采纳 / 标签 | Question、Answer、TagCatalog | E2 认识社区、E3 发起提问、E4 参与回答、E5 社区共建 |
| **course** | 支撑域 | 课程、班级、选课组织 | Course | E3（课程维度组织） |
| **reputation** | 核心域 | 声誉流水、量化学习参与 | ReputationLedger | E6 声誉成长 |
| **discovery** | 通用域 | 检索与热门发现（读模型） | 无（读模型，不拥有聚合） | E2（发现维度） |

## 二、上下文关系图

> 图例：箭头 = 依赖 / 数据流方向（谁消费谁的端口、谁持有谁的 ID）；编号对应第三节关系清单。

```
                      ┌────────────────────────────┐
                      │      shared（共享内核）      │
                      │  DeclarativeBase · 领域事件  │
                      │  认证原语 · 通用值对象        │
                      └──────────────▲─────────────┘
                                     │ ⑤ 共享内核（identity / qa / course 依赖 shared）
        ┌──────────┐                  ┌──┴───────┐                  ┌────────────┐
        │ identity │◀─────①──────────│    qa    │──────②──────────▶│ reputation │
        └──────────┘   消费认证原语    └─┬──────┘   领域事件（发布-订阅） └────────────┘
                        + author_id 引用│
                                       ├──────────────┐
                                       │ ③            │ ④
                                       │ course_id    │ 数据供给
                                       │ 引用（qa 持有）│ （读模型/事件流）
        ┌──────────┐                   │              │
        │  course  │◀──────────────────┘              └───────────────▶ ┌────────────┐
        └──────────┘                                                   │ discovery  │
                                                                       └────────────┘

  ① qa → identity：qa 消费 shared 认证原语（端口来自 identity），并持 author_id 引用用户
  ② qa → reputation：qa 发布 AnswerAccepted / VoteCast 等领域事件，reputation 订阅记账
  ③ qa → course：Question 持 course_id 引用课程（qa 依赖 course，不 import 其聚合对象）
  ④ qa → discovery：qa 供给持久化视图 / 事件流，discovery 只读建索引，不回写
```

## 三、关系清单（Context Map 关系类型）

| # | 上游 → 下游 | 关系模式 | 协作方式 | 说明 |
|:--|:---|:---|:---|:---|
| 1 | identity → qa | 客户-供应商（上游供身份） | qa 通过 `shared` 中的认证原语（JWT 校验、`get_current_user`）取得用户身份，并以 `author_id` 引用用户（不持有 User 聚合对象）；qa 不重复实现认证 | qa 是认证与身份引用的消费方；identity 变更接口需与 qa 协商 |
| 2 | qa → reputation | 发布语言 / 领域事件（发布-订阅） | qa 发布 `AnswerAccepted`、`VoteCast` 等事件；reputation 订阅消费并记账，不反向依赖 qa | 声誉计算解耦：投票/采纳不等待声誉落账（事件最终一致） |
| 3 | course → qa | 客户-供应商 | qa 中的问题以 `course_id`（ID 引用）关联课程；qa 不 import course 的聚合对象 | 弱关联：MVP 阶段问题可不挂课程 |
| 4 | qa → discovery | 客户-供应商（数据供给） | discovery 只读 qa 的持久化视图/事件流建索引；不回写 | discovery 为纯读模型，检索结果跳转 qa 详情 |
| 5 | identity / qa / course → shared | 共享内核 | 仅共享：DeclarativeBase、领域事件基类、认证原语、通用值对象 | 共享内容必须稳定且小；业务规则禁止放入 shared |

## 四、边界规则（评审要点）

1. **domain 层零框架依赖** —— 各上下文 domain 包不 import FastAPI / SQLAlchemy（ADR-002）
2. **跨上下文只经应用层** —— 不直连他域仓储；跨聚合协作 = 应用层编排 + 领域事件
3. **聚合间只以 ID 引用** —— Question 引用 `author_id`（identity）与 `course_id`（course），不持有对方聚合对象
4. **公共代码必须上收 `shared/`** —— 上下文之间禁止互相 import 私有实现
5. **reputation 是事件消费方** —— 声誉流水以 `event_id` 唯一索引保证幂等，事件重复投递不重复计分

## 五、上下文 ↔ 故事 ↔ 迭代对照

| 上下文 | 承载故事（ID） | 首次交付迭代 |
|:---|:---|:---|
| identity | R01–R04、L01–L04 | 迭代 1 起（L03/L04 迭代 5） |
| qa | Q01–Q04/Q06–Q08、A01–A02/A05、C01、V01–V04、T01–T02 | 迭代 1（WS）起，逐迭代扩展 |
| course | （MVP 仅 course_id 关联，无独立故事） | 迭代 4+（按需） |
| reputation | REP01–REP02 | 迭代 4 |
| discovery | Q07（筛选，读模型雏形） | 迭代 4 |
