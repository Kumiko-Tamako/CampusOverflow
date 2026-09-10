# Sprint 1 · 统一语言术语表（Ubiquitous Language / Glossary）

> 事件风暴产出（Lab 3 评分点：统一语言一致性）。≥30 条中英对照，全项目文档/代码/评审以此为准。
> 排序：通用建模术语 → 身份域 → 问答域 → 课程域 → 声誉域 → 发现域 → 流程术语。

## 一、通用建模术语（DDD）

| # | 中文 | 英文 | 定义 |
|:--|:---|:---|:---|
| 1 | 限界上下文 | Bounded Context | 领域模型的边界，边界内术语与规则自洽；本项目物理分包单位 |
| 2 | 聚合 | Aggregate | 一致性边界的对象簇，经根实体对外引用 |
| 3 | 聚合根 | Aggregate Root | 聚合的入口实体，外部只能持有根的 ID |
| 4 | 实体 | Entity | 有唯一标识、生命周期连续的对象 |
| 5 | 值对象 | Value Object | 无标识、以属性值判等、不可变的对象 |
| 6 | 领域事件 | Domain Event | 领域中已发生事实的表述，过去式命名（如 AnswerAccepted） |
| 7 | 仓储 | Repository | 聚合持久化的端口抽象，domain 定义接口、infrastructure 实现 |
| 8 | 应用服务 / 用例 | Use Case | 应用层编排单元，一个用例 = 一个业务动作 |
| 9 | 统一语言 | Ubiquitous Language | 团队共享的业务语言，代码/文档/沟通同词同义 |
| 10 | 防腐层 | Anti-Corruption Layer | 隔离外部模型入侵的转换层（本项目 qa 仅经 identity interfaces/api 公开供给面消费认证依赖，不触碰 identity 内部实现，即此角色的落地方式） |
| 11 | 共享内核 | Shared Kernel | 多上下文共享的公共模型子集（如 DeclarativeBase） |
| 12 | 幂等 | Idempotency | 同一操作重复执行结果不变；声誉流水以 event_id 唯一索引保证 |
| 13 | 不变式 | Invariant | 聚合内必须恒真成立的业务规则 |

## 二、身份与认证域（identity）

| # | 中文 | 英文 | 定义 |
|:--|:---|:---|:---|
| 14 | 用户 | User | 平台身份聚合根，学生或教师 |
| 15 | 学生 | Student | 以学号注册的用户角色 |
| 16 | 教师 | Teacher | 以工号注册的用户角色 |
| 17 | 学号 | Student ID | 学生唯一校园标识（值对象） |
| 18 | 工号 | Staff ID | 教师唯一校园标识（值对象） |
| 19 | 注册 | Registration | 创建账号的动作，学生/教师分流 |
| 20 | 登录 | Login | 凭账号密码换取令牌的认证动作 |
| 21 | 访问令牌 | Access Token | 15 分钟有效的 JWT，请求鉴权用 |
| 22 | 刷新令牌 | Refresh Token | 7 天有效、存 Redis 可吊销的续期凭证 |
| 23 | 角色 | Role | RBAC 中的权限集合标签（student / teacher） |
| 24 | 基于角色的访问控制 | RBAC (Role-Based Access Control) | 按角色判定接口权限的授权模型 |
| 25 | 密码哈希 | Password Hash | bcrypt 派生的密码存储形态，禁止明文 |

## 三、问答核心域（qa）

| # | 中文 | 英文 | 定义 |
|:--|:---|:---|:---|
| 26 | 问题 | Question | 提问者发布的求助内容，qa 首要聚合根 |
| 27 | 回答 | Answer | 针对问题的解答内容，Answer 聚合根 |
| 28 | 评论 | Comment | 附着于问题或回答的短讨论 |
| 29 | 投票 | Vote | 对问题/回答的赞成或反对，一人一对象一票 |
| 30 | 赞成票 | Upvote | 正向投票，声誉加分的触发源 |
| 31 | 反对票 | Downvote | 反向投票，声誉减分的触发源 |
| 32 | 采纳 | Acceptance | 提问者将某回答标记为最佳答案的动作 |
| 33 | 最佳答案 | Accepted Answer | 被采纳的回答，恒排答案区最前 |
| 34 | 标签 | Tag | 内容主题的值对象，同名唯一 |
| 35 | 标签目录 | Tag Catalog | 全站合法标签的集合，TagCatalog 聚合根 |
| 36 | 关闭问题 | Close Question | 提问者终结问题的动作；关闭后禁止投票与回答 |

## 四、课程域（course）

| # | 中文 | 英文 | 定义 |
|:--|:---|:---|:---|
| 37 | 课程 | Course | 教学组织单位，问题可挂课程 ID |
| 38 | 选课 | Enrollment | 学生与课程的关联关系 |

## 五、声誉域（reputation）

| # | 中文 | 英文 | 定义 |
|:--|:---|:---|:---|
| 39 | 声誉 | Reputation | 量化用户贡献的积分，由流水累加得出 |
| 40 | 声誉流水 | Reputation Ledger | 只追加的声誉变动账本，ReputationLedger 聚合根 |
| 41 | 流水行 | Ledger Entry | 一次声誉变动的记录，event_id 唯一保证幂等 |

## 六、发现域（discovery）

| # | 中文 | 英文 | 定义 |
|:--|:---|:---|:---|
| 42 | 检索 | Search | 按关键词/标签查找问题（读模型） |
| 43 | 热门问题 | Trending Questions | 按投票/热度排序的问题榜单 |

## 七、流程与工程术语

| # | 中文 | 英文 | 定义 |
|:--|:--|:---|:---|
| 44 | 事件风暴 | Event Storming | 以领域事件为线索的协作建模工作坊（本目录三份文档的产出方式） |
| 45 | 走查骨架 | Walking Skeleton | 端到端贯通的最小垂直切片（注册→登录→提问→列表→详情） |
| 46 | 迭代 | Iteration / Sprint | 固定时段的交付周期；本项目迭代 1 = 阶段 2（WS） |

---

**条目合计：46 条**（要求 ≥30）。术语与 `story-map.md` / `product-backlog.md` / `acceptance-criteria.feature` 用词逐一对应；新增术语（如关闭问题）须先入本表再入代码。
