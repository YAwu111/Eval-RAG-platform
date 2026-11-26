# API 契约

> 版本：v0.1（M0 设计稿）
> Base URL：`http://localhost:8000/api`
> 本文与 FastAPI 自动生成的 `/openapi.json` 同步维护；改接口必须同时改两处。

## 1. 通用约定

- 认证：**无**（个人单用户平台）。前端不发送 token。
- 内容类型：JSON 请求/响应；上传使用 `multipart/form-data`。
- ID：UUID v4 字符串。
- 时间：ISO 8601，UTC，例如 `2026-11-26T12:34:56Z`。
- 分页：`?limit=20&offset=0`，`limit` 默认 20，最大 100。
- 排序：列表默认 `created_at desc`，另有说明除外。

### 错误格式

所有非 2xx 响应统一信封。FastAPI 默认的 `HTTPException` 与 `RequestValidationError` 必须注册处理器，分别映射到 `NOT_FOUND`/`VALIDATION_ERROR` 等 code，禁止把 `{"detail": …}` 直接漏给前端：

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Collection not found",
    "details": {}
  }
}
```

| HTTP | code 示例 | 场景 |
|---|---|---|
| 400 | `INVALID_ARGUMENT` | 参数语义不合法 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `CONFLICT` / `RUN_IN_PROGRESS` | 重名、状态冲突、已有活动评测 run |
| 413 | `FILE_TOO_LARGE` | 上传超过 20MB |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | 非 txt/md/pdf/docx |
| 422 | `VALIDATION_ERROR` | Pydantic 校验失败 |
| 503 | `MODEL_UNAVAILABLE` | 模型未加载/显存不足 |
| 500 | `INTERNAL_ERROR` | 未捕获异常 |

## 2. 健康与概览

### `GET /health`

```json
{
  "status": "ok",
  "version": "0.1.0",
  "db": "ok",
  "models": {
    "embedding": "lazy",
    "reranker": "lazy",
    "judges": "lazy"
  }
}
```

`status` 为 `ok | degraded | down`；模型字段为 `lazy | ready | failed`。

### `GET /stats/overview`

```json
{
  "collections": 3,
  "documents": 12,
  "chunks": 486,
  "latest_run": {
    "id": "…",
    "status": "succeeded",
    "composite": 0.846,
    "finished_at": "2026-11-26T12:40:00Z"
  },
  "index": {
    "embedding_model": "BAAI/bge-m3",
    "dim": 1024,
    "reranker_model": "BAAI/bge-reranker-v2-m3"
  }
}
```

`latest_run` 无评测时为 `null`。

## 3. 知识库

### `GET /collections`

```json
{
  "items": [
    {
      "id": "…",
      "name": "检索与重排",
      "description": "混合检索、RRF、rerank 的设计与实验记录",
      "document_count": 6,
      "chunk_count": 312,
      "created_at": "2026-11-26T10:00:00Z",
      "updated_at": "2026-11-26T10:00:00Z"
    }
  ],
  "total": 3,
  "limit": 20,
  "offset": 0
}
```

### `POST /collections`

```json
{ "name": "检索与重排", "description": "可选" }
```

- 201 返回 collection；重名 409。

### `GET /collections/{collection_id}`

返回单个 collection，字段同上。

### `PATCH /collections/{collection_id}`

```json
{ "name": "新名字", "description": "新描述" }
```

字段均可选。

### `DELETE /collections/{collection_id}`

- 204；级联删除 documents / chunks。
- 若该 collection 的 chunk 被评测用例引用，仍删除，相关用例的 `relevant_chunk_ids` 会失效；MVP 不阻止，UI 需二次确认。

## 4. 文档

### `GET /collections/{collection_id}/documents`

查询参数：`status`（可选）、`limit`、`offset`。

```json
{
  "items": [
    {
      "id": "…",
      "collection_id": "…",
      "title": "混合检索设计规范 v3.2",
      "filename": "hybrid-retrieval.md",
      "mime": "text/markdown",
      "status": "ready",
      "error": null,
      "chunk_count": 128,
      "size_bytes": 18244,
      "created_at": "2026-11-26T10:01:00Z",
      "updated_at": "2026-11-26T10:01:20Z"
    }
  ],
  "total": 6,
  "limit": 20,
  "offset": 0
}
```

`status`：`queued | parsing | chunking | embedding | ready | failed`。

### `POST /collections/{collection_id}/documents`

`multipart/form-data`：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | file | 是 | `.txt .md .pdf .docx`，≤ 20MB |
| `title` | string | 否 | 缺省取文件名（去扩展名） |

响应 **202**：

```json
{
  "id": "…",
  "collection_id": "…",
  "title": "hybrid-retrieval",
  "filename": "hybrid-retrieval.md",
  "mime": "text/markdown",
  "status": "queued",
  "error": null,
  "chunk_count": 0,
  "size_bytes": 18244,
  "created_at": "2026-11-26T10:01:00Z",
  "updated_at": "2026-11-26T10:01:00Z"
}
```

前端轮询 `GET /documents/{id}` 直到 `ready/failed`。

### `GET /documents/{document_id}`

返回文档详情，字段同上；额外返回 `chunks_preview`（前 3 块，可选）。

### `DELETE /documents/{document_id}`

- 204；级联删除 chunks；collection 计数刷新。

## 5. 对话

### `POST /conversations`

```json
{ "title": "可选，缺省由首条提问生成" }
```

201 返回：

```json
{
  "id": "…",
  "title": "当 BM25 和向量召回冲突时…",
  "created_at": "…",
  "updated_at": "…"
}
```

### `GET /conversations`

`{items,total,limit,offset}`；item 含 `id/title/created_at/updated_at/last_message_preview`。

### `GET /conversations/{conversation_id}`

```json
{
  "id": "…",
  "title": "…",
  "created_at": "…",
  "updated_at": "…",
  "messages": [
    {
      "id": "…",
      "role": "user",
      "content": "当 BM25 和向量召回给出冲突证据时，reranker 如何权衡？",
      "citations": [],
      "trace": null,
      "model": null,
      "latency_ms": null,
      "created_at": "…"
    },
    {
      "id": "…",
      "role": "assistant",
      "content": "它不做加权平均……[1][2]",
      "citations": [],
      "trace": null,
      "model": "deepseek-chat",
      "latency_ms": 2840,
      "created_at": "…"
    }
  ]
}
```

### `POST /conversations/{conversation_id}/messages`

请求：

```json
{
  "content": "当 BM25 和向量召回给出冲突证据时，reranker 如何权衡？",
  "collection_ids": ["…"],
  "top_k": 6,
  "use_rerank": true
}
```

- `collection_ids` 省略时搜全部知识库；跨 collection 时先各自召回，再按归一化 BM25/向量分数合并后统一 RRF。
- `top_k` 1–12，默认 6；`use_rerank` 默认 true。它只决定送入答案的上下文条数，不改变评测口径。
- 同步等待检索 + 生成完成（MVP 无流式），超时 60s。

响应 201：assistant message

```json
{
  "id": "…",
  "conversation_id": "…",
  "role": "assistant",
  "content": "它不做加权平均。RRF 只融合两路召回的排名……[1][2]",
  "model": "deepseek-chat",
  "latency_ms": 2840,
  "token_usage": { "prompt": 2180, "completion": 320 },
  "citations": [
    {
      "index": 1,
      "chunk_id": "…",
      "document_id": "…",
      "document_title": "混合检索设计规范 v3.2",
      "heading_path": "H2 > 融合策略",
      "content": "RRF 只融合排名，不参与最终排序……",
      "score": 0.947,
      "rank": 1
    },
    {
      "index": 2,
      "chunk_id": "…",
      "document_id": "…",
      "document_title": "rerank-service / README.md",
      "heading_path": "Rerank",
      "content": "cross-encoder 对 (query, chunk) 逐对打分……",
      "score": 0.882,
      "rank": 2
    }
  ],
  "trace": {
    "query": "…",
    "rewritten": ["…"],
    "stages": [
      { "stage": "rewrite", "label": "QUERY REWRITE", "duration_ms": 2, "meta": { "variants": 1 } },
      { "stage": "sparse", "label": "BM25 / SPARSE", "duration_ms": 5, "meta": { "hits": 24 } },
      { "stage": "dense", "label": "DENSE / BGE-M3", "duration_ms": 9, "meta": { "hits": 24 } },
      { "stage": "fusion", "label": "RRF FUSION", "duration_ms": 2, "meta": { "k": 60, "candidates": 38 } },
      { "stage": "rerank", "label": "CROSS-ENCODER RERANK", "duration_ms": 9, "meta": { "top": 6, "mode": "model" } }
    ],
    "candidates": 38,
    "reranked": 6,
    "latency_ms": 27
  },
  "created_at": "…"
}
```

### `DELETE /conversations/{conversation_id}`

- 204；级联删除 messages。

## 6. 评测

### `GET /eval/sets`

```json
{
  "items": [
    {
      "id": "…",
      "name": "Golden-15",
      "description": "覆盖检索、冲突证据、拒答的 15 条人工用例",
      "case_count": 15,
      "created_at": "…"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### `POST /eval/sets`

```json
{ "name": "Golden-15", "description": "可选" }
```

201 返回 set。

### `GET /eval/sets/{set_id}/cases`

```json
{
  "items": [
    {
      "id": "…",
      "set_id": "…",
      "question": "bge-m3 的向量维度是多少？",
      "ground_truth": "1024 维。",
      "relevant_chunk_ids": ["…"],
      "meta": { "difficulty": "easy", "type": "fact" }
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0
}
```

### `POST /eval/sets/{set_id}/cases`

```json
{
  "question": "…",
  "ground_truth": "…",
  "relevant_chunk_ids": ["…"],
  "meta": {}
}
```

201 返回 case。MVP 只支持单条添加；批量导入后续用 JSONL。

### `DELETE /eval/cases/{case_id}`

- 204。

### `POST /eval/runs`

```json
{
  "set_id": "…",
  "top_k": 6,
  "retrieval_k": 24,
  "rrf_k": 60,
  "use_rerank": true,
  "concurrency": 1
}
```

`concurrency` 取值 1–3，默认 1。同一时间只允许一个 `queued|running` 的 run：已有活动 run 时返回 **409 `RUN_IN_PROGRESS`**。评测口径固定 `K=5`（Hit@5 / MRR@5 / CP@5），与 `top_k` 解耦。响应 **202**：

```json
{
  "id": "…",
  "set_id": "…",
  "status": "queued",
  "config": {
    "top_k": 6,
    "retrieval_k": 24,
    "rrf_k": 60,
    "use_rerank": true,
    "concurrency": 1
  },
  "metrics": null,
  "progress": { "total": 15, "completed": 0, "failed": 0 },
  "error": null,
  "started_at": null,
  "finished_at": null,
  "created_at": "…"
}
```

### `GET /eval/runs`

查询：`set_id`、`status`、`limit`、`offset`。

```json
{
  "items": [
    {
      "id": "…",
      "set_id": "…",
      "set_name": "Golden-15",
      "status": "succeeded",
      "metrics": {
        "hit_rate": 0.873,
        "mrr": 0.742,
        "context_precision": 0.681,
        "faithfulness": 0.914,
        "answer_relevance": 0.887,
        "retrieval_score": 0.779,
        "generation_score": 0.901,
        "composite": 0.846,
        "judge_failures": 0
      },
      "progress": { "total": 15, "completed": 15, "failed": 0 },
      "started_at": "…",
      "finished_at": "…",
      "created_at": "…"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

`metrics` 在 queued/running 时为 `null`。judge 失败时该用例的 `faithfulness/answer_relevance/composite` 为 `null`、`status=error`，不参与 run 均值；不要伪造成 0。空答案导致的“无 claim”记 `faithfulness=0` 且 `note="no_claims"`，与调用失败区分。

### `GET /eval/runs/{run_id}`

返回 run 详情，字段同上，外加 `config`、`error`。

### `GET /eval/runs/{run_id}/cases`

查询：`status`（pass/warn/fail/error）、`limit`、`offset`。

```json
{
  "items": [
    {
      "id": "…",
      "run_id": "…",
      "case_id": "…",
      "question": "它在上一次回答里说的 k 值是多少？",
      "ground_truth": "60。",
      "answer": "…",
      "status": "fail",
      "metrics": {
        "hit_rate": 0.0,
        "mrr": 0.0,
        "context_precision": 0.41,
        "faithfulness": 0.62,
        "answer_relevance": 0.55,
        "retrieval_score": 0.103,
        "generation_score": 0.585,
        "composite": 0.368,
        "note": null
      },
      "retrieved": [
        { "chunk_id": "…", "document_title": "…", "rank": 1, "score": 0.82 }
      ],
      "latency_ms": 3120,
      "error": null
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0
}
```

### `POST /eval/runs/{run_id}/cancel`

- 202；仅 queued/running 可取消。置 `cancel_requested=true`，runner 在当前用例结束后停止并置 `cancelled`；`progress` 保留已计数，未跑用例不创建。重复取消幂等返回 202。

## 7. 共享枚举

| 枚举 | 值 |
|---|---|
| DocumentStatus | queued, parsing, chunking, embedding, ready, failed |
| RunStatus | queued, running, succeeded, failed, cancelled |
| CaseStatus | pass, warn, fail, error |
| MessageRole | user, assistant |

## 8. 前端联调检查清单

每个页面完成时必须核对：

- [ ] 列表空态、加载态、错误态都有 UI。
- [ ] 长任务（入库、评测）轮询有停止条件与手动刷新。
- [ ] 所有时间按本地时区展示；相对时间用 `Intl.RelativeTimeFormat`。
- [ ] 分数 `null` 显示 `—`，不显示 `0`。
- [ ] 引用编号与正文 `[n]` 对应；点击引用定位到 trace 对应 chunk。
- [ ] 删除操作二次确认，并说明级联影响。
