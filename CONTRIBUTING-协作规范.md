# CONTRIBUTING.md —— CampusOverflow 协作规范

> 建议存放：仓库根目录 `CONTRIBUTING.md`

## 一、分支规范

- 功能分支：`feature/<issue号>-简短主题`，例如 `feature/1-question`
- 每个功能分支必须从**最新 main** 拉出；开发期间定期 `git fetch origin && git merge origin/main`
- 禁止直接向 main 提交；main 只保留测试通过、经过评审、可发布的内容

## 二、提交信息规范

格式：`type: 动词开头描述`

| type | 场景 |
|:---|:---|
| feat | 新功能 |
| fix | 缺陷修复 |
| test | 测试 |
| docs | 文档 |
| ci | CI/构建 |
| chore | 工程杂项 |

提交粒度：一次提交只做一件事，可独立回退。

## 三、Pull Request 规范

- 创建 PR 时必须关联 Issue：描述中写 `Closes #编号`
- 指定至少 1 名 Reviewer；**禁止自己审批自己的 PR**
- PR 描述写明：改动内容、测试结果（pytest/ruff/mypy）、联调影响
- CI 红灯时**在原分支追加修复提交**，不要新开 PR
- 合并方式：CI 通过 + 至少 1 个 Approve 后 Squash and merge

## 四、评审要求

- 拒绝只写 "LGTM"；至少给出 1 条可落地、可复现的意见
- 期望闭环：Request changes → 作者修改 → 重新评审 → Approve
- 评审关注点：后端看错误处理/幂等/安全；前端看 TS 规范/Hooks/可维护性
- 每周互评 ≥ 2 次 PR

## 五、质量门禁（合并前必须全部通过）

- ruff：0 错误
- mypy --strict：0 错误
- 测试：pytest 全部通过
- 覆盖率：整体 ≥ 70%，核心聚合 ≥ 90%
- 队友评审通过

## 六、版本发布

- 功能全部合并且 main 测试通过后，由仓库管理员发布 Release（当前目标 v1.0.0）
