# Sprint 1 回顾纪要（Retro）

> 建议存放：`docs/sprint/S1-回顾纪要.md`
> 主持：SM　参与者：PO、SM、Dev·后端、Dev·前端　日期：2026-09-10

## 一、本轮已完成（真实记录）

| 时间 | 内容 | 证据 |
|:---|:---|:---|
| 2026-09-07 | 工程骨架：pyproject、DDD 目录、最小应用、冒烟测试、CI、Compose | 仓库初始提交 |
| 2026-09-09 | PR #1 注册功能合并（User 聚合 + POST /auth/register，pytest 44 passed / ruff 0 / mypy 0） | PR #1 |
| 2026-09-10 | PR #2 登录+JWT 合并（双令牌 + RBAC，pytest 67 passed / ruff 0 / mypy 0） | PR #2 |

## 二、本轮暴露的问题（SM 记录）

1. 已有 PR #1/#2 由仓库所有者一人提交并直接合并，**缺少代码评审记录**——不满足实验"至少一次有效评审"要求，后续 PR 必须补上评审闭环；
2. 尚未建立 Issue / Milestone / 看板，Backlog 未落到 GitHub，任务状态无法追踪；
3. 分支命名已有 `feat/login`、`feat/register`，未严格遵循 `feature/<issue号>-主题`，后续统一；
4. README 冲突解决剧情（实验要求 #2 PR）尚未发生，需在后续 PR 中安排一次真实冲突并规范解决。

## 三、改进措施（SM 推动落实）

| 措施 | 负责人 | 截止 |
|:---|:---|:---|
| 建 3 个 Issue + Milestone + 看板，任务状态 24h 更新 | SM | 本周 |
| 后续每个 PR 关联 Issue、指定 Reviewer、至少一次有效评审 | 全员 | 每个 PR |
| 统一分支命名与提交信息规范（见 CONTRIBUTING.md） | 全员 | 即日起 |
| 安排一次 README 冲突并提交 fix 解决 | 相关 Dev | 下一个 PR |
| 补团队证据索引表 | SM | 提交前 |

## 四、下次迭代保持

- 门禁执行良好（pytest/ruff/mypy 全绿）
- openapi.json 契约先行机制有效
