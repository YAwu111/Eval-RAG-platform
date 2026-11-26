# LLMDOC — TRACE // RAG Eval Workbench

> 单文件项目压缩上下文。给 reviewer / subagent 冷启动用：先读本文，再按需读源码。
> 结构参考 [TokenRollAI/llmdoc](https://github.com/TokenRollAI/llmdoc) 的“知识面”思路，但本项目刻意保持一个文件。
> 更新时间：2026-11-26 · 里程碑：M0

## 1. 目标

做一个**个人使用的 RAG 知识对话 + 评估工作台**：

1. 上传文档 → 切分 → 向量化 → 混合检索 → 重排 → 带引用回答。
2. 用固定评测集算 Hit Rate@K、MRR、Context Precision、Faithfulness、Answer Relevance。
3. 前端沿用已选定的 **A · KERNEL ARCADE**（8-bit 霓虹实验室）：像素 / 代码雨 / CRT，但中文长文必须可读。
4. 单用户，无登录。前端 React + Zustand + shadcn/ui + Tailwind + axios；后端 FastAPI + PostgreSQL(pgvector)。

**非目标**：多租户、RBAC、分布式队列、流式 token、对象存储、多语言 UI。

## 2. 当前状态

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M0 | 仓库、架构/API 文档、LLMDOC、设计定稿 | ✅ |
| M1 | FastAPI 骨架、DB 模型、Alembic、健康检查 | ⏳ 下一个 |
| M2 | 入库 + 稠密/稀疏检索 + RRF + 重排 | ⏳ |
| M3 | 对话 API + 引用 + trace + 前端联调 | ⏳ |
| M4 | 评测 runner + HF judge | ⏳ |
| M5 | 前端三视图 + 动效 | ⏳ |

**M0 没有业务代码**。不要假设 `apps/api` 或 `apps/web` 已存在。

## 3. 目录与职责

```text
apps/api/app/
  main.py               create_app、lifespan、CORS、router
  core/                 config(pydantic-settings)、logging、errors
  db/                   engine/session/base/models
  api/routes/           health, stats, collections, documents, conversations, eval
  schemas/              Pydantic 请求/响应
  services/
    ingest.py           解析 → 切分 → 向量化 → 入库
    retrieval/          dense.py, sparse.py, fusion.py, rerank.py, pipeline.py
    answer/             prompts.py, deepseek.py, extractive.py
    evaluation/         metrics.py, judges.py, runner.py
    storage.py          本地 uploads
  workers/              进程内后台任务注册
apps/web/src/
  app/                  router, layout
  components/ui/        shadcn 源码
  components/brand/     CodeRain, PixelMascot, Scanlines
  features/chat|corpus|eval/
  stores/               app/chat/corpus/eval
  lib/api.ts            axios 单例 + 类型
  styles/               tokens.css, globals.css
```

设计原型（只读参考，不要当生产代码）：`design/concept-a.html`。

## 4. 数据模型（表）

- `collections(id, name, description, document_count, chunk_count, index_version, timestamps)`
- `documents(id, collection_id, title, filename, mime, status, error, chunk_count, size_bytes, meta)`
- `chunks(id, document_id, collection_id, content, search_text, chunk_index, heading_path, token_count, embedding vector(1024), meta)`
- `conversations(id, title, timestamps)`
- `messages(id, conversation_id, role, content, citations jsonb, trace jsonb, model, latency_ms, token_usage)`
- `eval_sets(id, name, description, case_count)`
- `eval_cases(id, set_id, question, ground_truth, relevant_chunk_ids uuid[], meta)`
- `eval_runs(id, set_id, status, config jsonb, metrics jsonb, error, started_at, finished_at)`
- `eval_case_results(id, run_id, case_id, answer, retrieved_ids, metrics jsonb, status, latency_ms, trace jsonb, error)`
- `judge_cache(id, key unique, kind, model, score, raw, created_at)`

枚举：

```text
DocumentStatus: queued parsing chunking embedding ready failed
RunStatus:      queued running succeeded failed cancelled
CaseStatus:     pass warn fail error
```

## 5. 不可破坏的契约

1. **引用编号**：assistant 正文中的 `[n]` 对应 `citations[n-1]`；`citations[].index` 从 1 连续。
2. **trace stage 名称**：`rewrite / sparse / dense / fusion / rerank`，前端按此渲染；未知 stage 忽略不报错。
3. **分数为 null**：judge 失败时 `faithfulness/answer_relevance=null`，禁止写成 0。
4. **评测集真值**：Hit/MRR/CP 只认 `eval_cases.relevant_chunk_ids`，不靠 LLM 猜。
5. **API 错误包**：`{"error":{"code","message","details"}}`，前端按 `code` 分支。
6. **密钥只在服务端**：DeepSeek/HF token 只进 `.env`；前端 bundle 不得出现。
7. **评分公式**：
   - `retrieval = .4*hit + .35*mrr + .25*cp`
   - `generation = .5*faithfulness + .5*answer_relevance`
   - `composite = .45*retrieval + .55*generation`
   - 单用例：`pass ≥ .70`，`warn ≥ .50`，否则 `fail`。
8. **RRF**：`score = Σ 1/(60 + rank)`，按 chunk_id 去重，保留各路 rank。
9. **模型懒加载**：启动不加载权重；首次调用加载；`HF_HOME=D:\hf-cache`，不要写 C 盘。
10. **评测口径**：Hit@5 / MRR@5 / CP@5 固定 K=5；judge 失败该用例 `status=error`、分数 `null`，run 记 `judge_failures`；空答案 `faithfulness=0` + `note="no_claims"`。

## 6. API 速查

Base：`http://localhost:8000/api`，无鉴权。

```text
GET    /health
GET    /stats/overview
GET    /collections                 POST /collections
GET    /collections/{id}            PATCH/DELETE
GET    /collections/{id}/documents  POST (multipart)
GET    /documents/{id}              DELETE
POST   /conversations               GET /conversations
GET    /conversations/{id}          DELETE
POST   /conversations/{id}/messages
GET    /eval/sets                   POST /eval/sets
GET    /eval/sets/{id}/cases        POST; DELETE /eval/cases/{id}
POST   /eval/runs                   GET /eval/runs
GET    /eval/runs/{id}              GET /eval/runs/{id}/cases
POST   /eval/runs/{id}/cancel
```

完整字段见 `docs/API.md`；实现时以 FastAPI OpenAPI 为准，两者必须同步。

## 7. 核心流程

**入库**：multipart → document(queued) → 202 → 后台解析 → 切分(512/64) → BGE-M3 → chunks → ready。

**问答**：rewrite(可选) → dense top24 + BM25 top24 → RRF 60 → rerank top6 → LLM/抽取式 → 保存 message + trace + citations。

**评测**：POST run(202, queued) → asyncio task → 每用例走同一问答链路 → 代码指标 → NLI Faithfulness + embedding Relevance → 写 case result → 汇总 metrics → succeeded。评测口径固定 K=5，`top_k` 只影响答案上下文；同一时间只允许一个 `queued|running` run，冲突返回 409 `RUN_IN_PROGRESS`。

## 8. 模型

| 模型 | 用途 | 状态 |
|---|---|---|
| `BAAI/bge-m3` | embedding 1024d | 已缓存 D 盘 |
| `BAAI/bge-reranker-v2-m3` | cross-encoder 重排 | 已缓存 D 盘 |
| `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` | Faithfulness NLI | 首次下载 |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Answer Relevance | 首次下载 |
| `deepseek-chat` | 生成 | 通过 `.env` 的 `LLM_API_KEY` 配置 |

DeepSeek 走 OpenAI 兼容 `https://api.deepseek.com`；无 key 时 `ExtractiveAnswerer` 兜底，UI 标 `EXTRACTIVE`。

## 9. 命令（M1 起生效）

```bash
docker compose up -d db
cd apps/api
python -m venv .venv && .venv\Scripts\activate
pip install -e ".[ml]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
python scripts/seed.py

cd apps/web
pnpm install
pnpm dev
```

环境变量见 `.env.example`；真实 `.env` 被 gitignore。

## 10. 前端约定

- 路由：`/chat`、`/corpus`、`/eval`、`/eval/runs/:id`；`/` 重定向。
- store 只存 UI 状态与当前资源；请求集中在 `lib/api.ts`；组件不直接 axios。
- 轮询：文档 2s，评测 run 2s；切换路由/卸载必须清理。
- 分数 null → `—`；时间本地化；删除二次确认。
- 视觉 tokens 见 `design/concept-a.html`：`#07070c / #c8ff3d / #ff3d9a / #38e8ff`；Silkscreen 只用于标题与数字。
- `prefers-reduced-motion` 时关闭代码雨与闪烁。

## 11. Review 重点（给只读 subagent）

按 P0/P1/P2 输出，不要改代码：

**P0（必须修）**
- 跨模块契约破坏：引用编号、trace stage、错误包、null 分数。
- 密钥/配置泄漏到前端或仓库。
- SQL 注入、路径穿越、上传任意文件执行。
- 评测公式与 `docs/ARCHITECTURE.md §7.1` 不一致。
- 后台任务吞异常导致 run 永远 running。

**P1（应修）**
- 路由里写业务逻辑、service 依赖 FastAPI。
- N+1 查询、缺索引、全表加载 chunks。
- 阻塞事件循环（同步模型调用未 `to_thread`）。
- 前端重复请求、轮询泄漏、缺空/错/加载态。
- API 文档与实现不一致。

**P2（可记）**
- 命名、注释、重复代码、可读性。
- 动效性能、响应式断点。
- 测试缺口。

## 12. 未决风险

- 进程内 BM25 索引在 48k chunks 的内存与冷启动；规模上去换 OpenSearch。
- 进程内后台任务重启丢 run；后续 Celery/Arq。
- 本地 judge 模型首次下载约 1GB，显存与启动时间需实测。
- DeepSeek 返回的 citation 可能不守格式，需要后端校验/回填。
- 评测 ground truth 需要人工标注，种子集只有 15 条，结论不能外推。
