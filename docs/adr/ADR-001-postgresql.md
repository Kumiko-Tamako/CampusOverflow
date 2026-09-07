# ADR-001: 采用 PostgreSQL 16 替代课程默认 MySQL 8

- 状态：已接受
- 日期：2026-09-07
- 关联阶段：阶段 0（工程重启）

## 背景

课程参考技术栈默认使用 MySQL 8 作为主数据库。本项目是校园问答平台：问题/答案正文需要富元数据存储（JSONB）、按标签与内容检索是核心功能（全文检索）、整体技术栈基于 FastAPI 全异步（需要与 SQLAlchemy 2.0 async 配套的异步驱动）。

## 决策

采用 **PostgreSQL 16**（Docker 镜像 `postgres:16-alpine`）作为唯一主数据库，驱动使用 `asyncpg`，迁移使用 Alembic。

理由：

1. **JSONB 原生支持** —— 问题元数据、扩展字段无需 EAV 或单独表
2. **全文检索内置** —— MVP 阶段零额外依赖实现搜索，避免过早引入 Elasticsearch
3. **异步生态完整** —— `asyncpg` 是 SQLAlchemy 2.0 async 官方推荐路径，性能优于 MySQL 异步方案
4. **约束与事务能力更强** —— 复合唯一约束（投票幂等）、部分索引（声誉流水幂等）直接落地

## 后果

正面：检索与异步能力开箱即用；DDD 战术建模所需的约束表达力更强。

负面/代价：

1. 与课程默认栈不同，需要自行承担运维责任 —— 已由 Docker Compose 编排覆盖（db 服务 + 命名卷 + healthcheck）
2. 团队需适应 PostgreSQL 方言与工具链（psql / pg_isready）
3. SQL 部分不能照搬课程示例，需按 PG 语法改写
