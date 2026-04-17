# 新功能：智能客服智能体（`power_bank/app/AI`）

## 背景

后端新增智能客服能力，用于回答用户常见问题（规则/流程）以及部分需要查询的业务问题。

## 功能点

- 新增问答接口：`POST /api/assistant/ask`
- 智能体支持工具调用：
  - SQL 查询（如余额、订单等）
  - RAG 检索（如押金、计费、退款等规则说明）
- 智能体提示词与业务文本外置到 `power_bank/app/AI/data/`

## 接口说明

### `POST /api/assistant/ask`

- 请求 JSON：`{ "username": "可选", "question": "必填" }`
- 响应 JSON：`{ "answer": "..." }` 或 `{ "message": "..." }`
- 代码位置：`power_bank/app/AI/agent/routes.py`

## 项目结构（新增模块）

```
power_bank/app/AI/
  agent/             # 智能体入口与工具
  data/              # 提示词与业务文本
  llm/               # LLM 封装（意图/SQL 等）
  rag/               # RAG：向量检索与摘要服务
  modle/             # 模型工厂（读取环境变量）
  utils/             # 文件/路径/日志工具
```

## 实现要点（简述）

- `agent/routes.py` 接收请求并调用 `UserAssistantAgent.ask(...)`
- `agent/agent.py` 组装：提示词（`data/sys_prompt.md`）+ 工具（`agent/tools.py`）+ 模型（`modle/factory.py`）
- 需要规则类回答时，通过 `rag/` 检索相关文本后再生成回复

## 示例

### 示例 1：规则类问题

- `POST /api/assistant/ask`
- body：`{"username":"test_user","question":"押金什么时候退？"}`
- 返回示例：`{"answer":"...（关于押金退还规则的说明）..."}`

### 示例 2：查询类问题

- `POST /api/assistant/ask`
- body：`{"username":"test_user","question":"我当前余额多少？"}`
- 返回示例：`{"answer":"...（返回当前余额的自然语言回答）..."}`

### 示例 3：多轮/追问（同一用户）

- `POST /api/assistant/ask`
- body：`{"username":"test_user","question":"我刚才那笔订单为什么扣费？"}`
- 返回示例：`{"answer":"...（结合订单/计费规则进行解释）..."}`


