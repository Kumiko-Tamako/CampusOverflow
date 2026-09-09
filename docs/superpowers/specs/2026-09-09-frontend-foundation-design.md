# CampusOverflow 前端基础设计

## 目标

在 `frontend/` 建立符合团队分工方案和 Lab 5 要求的 React 18 + TypeScript 5 工程，先用 mock 数据跑通 Walking Skeleton 的页面流程，再通过 `openapi.json` 接入 FastAPI。

第一阶段页面范围：

- 登录与注册页面
- 问题列表 `/questions`
- 发布问题 `/questions/new`
- 问题详情 `/questions/:id`

## 技术选择

- Vite + React 18 + TypeScript 5
- TypeScript `strict` 与 `noUncheckedIndexedAccess`
- Ant Design 5 作为初始 UI 组件库
- `react-router-dom` 负责路由
- Zustand 负责客户端登录状态
- TanStack Query 负责问题数据查询和缓存
- Axios 作为后续真实 API 客户端
- Vitest + React Testing Library 负责组件测试
- Playwright 负责 Walking Skeleton 端到端冒烟测试
- ESLint、Prettier、Husky + lint-staged 负责本地质量门禁

## 目录边界

```text
frontend/
├── src/
│   ├── api/          # Axios 配置、API 服务和契约适配
│   ├── components/   # 可复用 UI 组件
│   ├── hooks/        # Query 和业务 Hooks
│   ├── pages/        # 路由页面
│   ├── router/       # 路由表和访问控制
│   ├── stores/       # Zustand 客户端状态
│   └── features/     # auth/questions 的领域 UI 与 mock 数据
├── e2e/              # Playwright 冒烟流程
└── tests/            # 测试公共配置
```

页面只通过 `hooks` 获取数据，不直接依赖 mock 存储或 Axios 细节。后端接口完成后，只替换 `api` 层和契约类型，页面交互保持不变。

## 数据流

```text
页面 -> Hook -> service -> mock 数据（当前）
                    |
                    -> Axios + openapi 生成客户端（联调后）
```

发布问题成功后，使用 QueryClient 使问题列表失效并重新获取，确保新问题立即可见，满足 US-Q04。

## 验收标准

1. `pnpm dev` 可以启动前端并访问路由。
2. 访客可以查看问题列表和详情。
3. 登录状态下可以进入发布问题页；未登录访问时跳转登录页。
4. 发布问题后跳转详情，并能在列表看到新问题。
5. 空数据、加载中、表单错误和请求错误都有可见反馈。
6. `pnpm lint`、`pnpm typecheck`、`pnpm build` 全部通过。
7. Playwright 冒烟流程覆盖“登录 → 发布问题 → 查看详情”。
8. 前端检查加入 GitHub Actions；不提交 `.env` 或令牌。

## 暂不实现

- 回答、投票、采纳、评论、标签和声誉页面，留到后续 Sprint。
- 在没有后端 `openapi.json` 前猜测真实 API 字段。
- 首阶段引入 Tailwind；Ant Design 已满足当前 UI 组件需求，后续有明确视觉需求再加入。
