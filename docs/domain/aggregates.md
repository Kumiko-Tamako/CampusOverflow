# Sprint 1 · 聚合清单（Aggregates）

> 事件风暴产出（Lab 3 评分点：聚合边界与不变式）。
> 设计原则：聚合刻意收小、跨聚合只以 ID 引用、事务边界清晰优先（见 `context-map.md` 边界规则）。

## 一、聚合总览

| 上下文 | 聚合 | 根实体 | 包含对象 | 对应故事 |
|:---|:---|:---|:---|:---|
| identity | **User** | User | 实体：User<br>值对象：StudentId / StaffId / Email / PasswordHash | R01–R04、L01–L04 |
| qa | **Question** | Question | 实体：Question<br>值对象：Title / Body<br>实体：Vote（题票）/ Comment（题评） | Q01–Q08、V01（题）、V02、C01（题评） |
| qa | **Answer** | Answer | 实体：Answer / Vote（答票）/ Comment（答评） | A01–A05、C01（答评）、V01（答）、V03/V04 |
| qa | **TagCatalog** | TagCatalog | 值对象：Tag（集合） | T01、T02、Q03（合法性校验源） |
| course | **Course** | Course | 实体：Course / Enrollment | （MVP 仅 course_id 弱关联） |
| reputation | **ReputationLedger** | ReputationLedger | 实体：LedgerEntry（流水行） | REP01、REP02 |

> qa 内的 Comment 按挂载对象拆分：题评归属 Question 聚合、答评归属 Answer 聚合——评论生命周期跟随宿主，避免第三聚合。

## 二、聚合详情与不变式

### 1. User 聚合（identity）

- **根**：`User`
- **值对象**：`StudentId`（学号）、`StaffId`（工号）、`Email`、`PasswordHash`
- **不变式**：
  1. 密码必须以 bcrypt 哈希存储，任何路径不得保存明文
  2. 学号/工号全局唯一；邮箱全局唯一（R03）
  3. 密码强度：≥8 位且同时含字母与数字（R04）
  4. 身份二选一：学生（学号）或教师（工号），注册时确定（R01/R02）
- **领域事件**：`UserRegistered`

### 2. Question 聚合（qa）

- **根**：`Question`
- **包含**：`Title`、`Body` 值对象；`Vote` 实体（限本题票）、`Comment` 实体（题评）
- **对外 ID 引用**：`author_id` → identity.User；`course_id`（可选）→ course.Course
- **不变式**：
  1. 标题非空；正文非空（Q01）
  2. 标签至多 5 个，且必须存在于 TagCatalog（Q03——跨聚合校验经应用层）
  3. 发布后立即可见（Q04）
  4. 已关闭问题：禁止再投票（V02）、禁止新增回答；编辑仅限提问者（Q08）
  5. 已采纳答案的问题不可关闭（Q08 × V03 联动）
- **领域事件**：`QuestionPublished`、`QuestionClosed`、`VoteCast`（题票）

### 3. Answer 聚合（qa）

- **根**：`Answer`
- **包含**：`Vote` 实体（限本答票）、`Comment` 实体（答评）
- **对外 ID 引用**：`question_id` → qa.Question；`author_id` → identity.User
- **不变式**：
  1. 必须挂载于存在且未关闭的问题（A01）
  2. 正文非空；编辑仅限回答者本人（A02）
  3. 同一用户对同一回答仅一票（复合唯一约束）（V01）
  4. 被采纳的回答不可删除（V03）
  5. 展示排序：已采纳恒排最前，其余按票数从高到低（V04/A05，验收标准已钉死）
- **领域事件**：`AnswerPosted`、`AnswerAccepted`、`VoteCast`（答票）

### 4. TagCatalog 聚合（qa）

- **根**：`TagCatalog`（目录本身为聚合根，持标签集合）
- **值对象**：`Tag`（同名唯一）
- **不变式**：
  1. 目录内标签同名唯一，大小写不敏感（T02）
  2. 标签无需预审核，随用随建（T02）
  3. Question 引用标签必须指向目录内已存在的 Tag（Q03 合法性）
- **说明**：T02"同名唯一"是本聚合不变式而非独立故事（见 backlog INVEST 归并决策）

### 5. Course 聚合（course）

- **根**：`Course`
- **包含**：`Enrollment` 实体（选课关系）
- **不变式**：
  1. 课程编号唯一
  2. 选课关系 = 学生 × 课程，同一学生同一课程仅一条
- **说明**：MVP 阶段 qa 仅以 `course_id` 弱关联本聚合，无独立故事；扩展预留

### 6. ReputationLedger 聚合（reputation）

- **根**：`ReputationLedger`（按用户一本账）
- **包含**：`LedgerEntry`（流水行：event_id / 变动值 / 事由 / 时间）
- **不变式**：
  1. `event_id` 唯一索引——同一事件重复投递只记一次（幂等）（REP01）
  2. 只追加不修改：流水行生成后不可变更（审计要求）
  3. 账面声誉值 = 流水累加，不允许直接改总值
- **事件来源（订阅）**：`VoteCast`（投票加减分）、`AnswerAccepted`（采纳加分）
- **领域事件（发布）**：`ReputationChanged`

## 三、跨聚合协作（应用层编排）

| 编排场景 | 参与聚合 | 协作方式 |
|:---|:---|:---|
| 发布问题带标签 | Question + TagCatalog | UseCase 先查 TagCatalog 校验标签合法，再创建 Question（同一事务） |
| 采纳最佳答案 | Answer + Question | UseCase 校验提问者身份与回答归属 → Answer 标记采纳 → Question 记录采纳状态 → 发布 `AnswerAccepted` |
| 投票计入声誉 | Question/Answer（发事件）→ ReputationLedger | 事件异步订阅：Ledger 以 event_id 幂等记账，不阻塞投票主流程 |

## 四、聚合 ↔ 迭代交付对照

| 迭代 | 新增/扩展聚合 |
|:---|:---|
| 迭代 1（WS） | User（R01–R04/L01–L02）、Question（Q01/Q04，暂不含 Vote） |
| 迭代 2 | Question+Vote、Answer（A01/A02/V01）、票数排序（A05） |
| 迭代 3 | Answer 采纳状态 + `AnswerAccepted`（V03/V04）、Comment（C01：题评挂 Question、答评挂 Answer） |
| 迭代 4 | TagCatalog（Q03/T01/T02）、ReputationLedger（REP01/REP02）、Course 弱关联启用 |
| 迭代 5 | Question 关闭态（Q08）、V02 关闭禁投票 |
