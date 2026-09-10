# 3 个 Issue 创建模板

> 用途：复制到 GitHub 仓库 Issues → New issue 逐个创建。
> 当前 Sprint 建议：`Sprint 1`（建 Milestone 后挂到其下）。
> 提示：已有 PR #1/#2（注册、登录）未关联 Issue；后续 PR 必须 `Closes #编号` 关联以下 Issue。

---

## Issue 模板 1：qa 模块——提问功能

- **标题**：feat(qa): 提问功能（POST /questions + Question 聚合 + 列表/详情）
- **Label**：type:feature　**Assignee**：Dev·后端　**Milestone**：Sprint 1
- **描述**：
  - 后端：Question 聚合（含 Vote）、POST /questions 提问接口、按课程/标签/时间列表与详情；
  - 契约：完成一组接口即提交 `openapi.json`；
  - 前端：基于 codegen 实现提问表单与问题列表/详情页（接口未就绪用 mock 先行）；
  - 测试：后端 pytest 覆盖领域与接口，前端组件测试。
- **验收标准（DoD）**：
  - [ ] 提问、列表、详情接口可用，openapi.json 已更新
  - [ ] 前端提问→列表→详情主流程 30 秒内可演示（录屏）
  - [ ] 门禁：ruff 0 / mypy --strict 0 错 / 覆盖率达标 / CI 绿
  - [ ] PR 关联本 Issue，至少一次有效评审后合并

---

## Issue 模板 2：qa 模块——回答与采纳

- **标题**：feat(qa): 回答、采纳与评论（answer + accept + comment）
- **Label**：type:feature　**Assignee**：Dev·后端　**Milestone**：Sprint 1
- **描述**：
  - 后端：Answer 聚合、回答/采纳/评论接口，与 Question 关联；
  - 契约：更新 `openapi.json`；
  - 前端：回答区、采纳标记、评论交互；
  - 测试：领域与接口测试 + e2e 冒烟。
- **验收标准（DoD）**：
  - [ ] 回答、采纳、评论接口可用，openapi.json 已更新
  - [ ] 前端回答与采纳交互可演示
  - [ ] 门禁全绿，PR 关联本 Issue 并经有效评审合并

---

## Issue 模板 3：协作基建——看板、ADR 与协作规范（SM 认领）

- **标题**：docs(team): 看板搭建、ADR 归档与协作规范（SM）
- **Label**：type:docs　**Assignee**：SM　**Milestone**：Sprint 1
- **描述**：
  - GitHub Projects 看板（Backlog/Todo/In Progress/Review/Done）搭建并关联本仓库；
  - `docs/team/`（团队章程、角色承诺书）、`docs/adr/0001` 归档；
  - 根目录 `CONTRIBUTING.md` 协作规范（分支/提交/PR/评审/门禁）；
  - 团队证据索引表（Issue/PR/Commit/Actions/Release 链接）。
- **验收标准（DoD）**：
  - [ ] 看板可见且任务状态 24h 内更新
  - [ ] ADR ≥ 1 份、团队文档齐全并入库
  - [ ] 证据索引表链接完整
  - [ ] 本 PR 关联本 Issue，经组员评审后合并（SM 自己的 PR 由组员审）
