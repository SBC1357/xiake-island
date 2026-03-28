# 侠客岛 - 一期前端触发设置页

## 启动命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 生产构建
npm run build

# 运行测试
npm run test:run

# 代码检查
npm run lint
```

## 环境配置

创建 `.env` 文件配置 API 地址：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

默认值为 `http://127.0.0.1:8000`。

## 一期开放能力

### 触发目标

| 目标 | 接口 | 说明 |
|------|------|------|
| `opinion` | `POST /v1/opinion/generate` | 观点生成 |
| `semantic_review` | `POST /v1/review/semantic` | 语义审核 |
| `article` | `POST /v1/workflow/article` | 文章工作流 |

### 页面能力

- **目标切换区**：在 opinion / semantic_review / article 三者之间切换
- **本地草稿**：每个目标独立保存草稿到浏览器 localStorage
- **草稿操作**：
  - "清空当前草稿" → 回到空白状态（所有字段为空）
  - "恢复系统默认" → 回到预填默认值（如 audience 预填"医学专业人士"）
- **参数表单**：各目标专用表单
- **执行区**：手动触发执行，显示执行状态
- **结果区**：展示当前执行返回结果
- **最近执行区**：当前会话内最近几次执行摘要

### 关键约束

1. **context_metadata 必须是 JSON 对象**
   - 空文本：有效，表示不传递
   - JSON 对象：有效
   - 数组、字符串、数字、布尔值、null：无效

2. **article 工作流不暴露 semantic_review.content**
   - 审核内容由工作流自动从观点生成结果中提取

3. **草稿仅保存在浏览器本地**
   - 不跨设备同步
   - 不服务端保存

## 未开放能力（二三期）

- 定时触发 / 条件触发
- 动态能力目录
- 通用 schema 低代码表单平台
- 自动化规则编排
- 运营后台
- 服务端配置中心
- 历史任务中心
- 真实 LLM 接入

## 技术栈

- Vite 8
- React 19
- TypeScript 5.9
- Vitest 4 + React Testing Library

## 项目结构

```
frontend/
├── src/
│   ├── api/           # API 客户端
│   ├── components/    # UI 组件
│   │   ├── forms/     # 表单组件
│   │   ├── results/   # 结果视图
│   │   └── ui/        # 基础 UI 组件
│   ├── hooks/         # React Hooks
│   ├── pages/         # 页面组件
│   ├── test/          # 测试文件
│   └── types/         # 类型定义
├── .env               # 环境变量
├── vite.config.ts     # Vite 配置
├── vitest.config.ts   # 测试配置
└── package.json
```

## 测试覆盖

| 测试文件 | 测试数量 | 覆盖内容 |
|----------|----------|----------|
| ContextMetadataEditor.test.tsx | 10 | 空文本、JSON对象、数组、字符串、数字、布尔值、null、无效语法 |
| ArticleWorkflowConfigForm.test.tsx | 8 | 不暴露 content 字段、说明文字、表单边界 |
| useDraftStorage.test.ts | 6 | clearDraft vs resetToDefault 区分 |

---

**本次完成的是一期前端收口包，不包含真实 LLM 接入，不包含二三期自动化平台能力。**
