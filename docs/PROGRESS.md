# CampusOverflow 进度表

> 里程碑状态对照，随开发推进更新。

## 里程碑总览

| 阶段 | 周次 | 主题 | 状态 | 关键验收 |
|:---|:---|:---|:---|:---|
| 阶段 0 | W1–W2 | 工程重启 | **完成** | 本地门禁全绿；GitHub Actions 变绿 |
| 阶段 1 | W3–W5 | Sprint 1 文档 | 未开始 | 覆盖 Lab 2+3 全部提交物 |
| 阶段 2 | W7–W9 | Walking Skeleton | 未开始 | 注册→登录→提问→列表→详情贯通；覆盖率 ≥70% |
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
| 0.8 | 门禁全绿 + 首次提交 + CI 变绿 | 进行中 |
| 0.9 | 项目文档（PROGRESS + ADR-001/002） | 完成 |

## 相关决策

- [ADR-001 采用 PostgreSQL 16 替代课程默认 MySQL 8](adr/ADR-001-postgresql.md)
- [ADR-002 限界上下文纵切物理分包](adr/ADR-002-context-partition.md)
