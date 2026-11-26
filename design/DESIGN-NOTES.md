# TRACE // — 设计方向说明

> RAG 知识对话 + 评估工作台 · 四版概念设计
> 2026-11-26 · 供方向选择使用

---

## 0. 当前状态

四个方向都已经是**可交互的 HTML 原型**，不是静态效果图：

| # | 方向 | 文件 | 视图 |
|---|------|------|------|
| A | KERNEL ARCADE | `design/concept-a.html` | 对话 / 知识库 / 评测 |
| B | GROUNDTRUTH | `design/concept-b.html` | 对话 / 标本 / 仪表 |
| C | SIGNAL GARDEN | `design/concept-c.html` | 冠层 / 种子库 / 花期 |
| D | CHROMA//DECK | `design/concept-d.html` | 直播 / 资料库 / 评分 |

入口：`design/index.html`（四版对比与选择页）。

每个原型都包含：真实密度的中文内容、检索链路追踪、五项指标、评测用例表、动画与页面切换。截图在 `design/screenshots/`。

**方向已选定 A · KERNEL ARCADE**；M0 完成工程文档，React 实现从 M1 起按模块推进。B/C/D 保留为选型档案，不再改动。

---

## 1. 四版设计立场

### A · KERNEL ARCADE — 8-bit 霓虹实验室

- **一句话**：把 RAG 管线做成一台街机，评测分数是计分板。
- **视觉**：近黑底 `#07070c`，荧光绿 `#c8ff3d`、荧光粉 `#ff3d9a`、青 `#38e8ff`；Silkscreen 像素标题 + Space Grotesk + IBM Plex Mono；canvas 代码雨、像素星星、CRT 扫描线、会眨眼的小怪物。
- **信息结构**：左侧聊天，右侧检索链（rewrite → BM25 → dense → RRF → rerank），底部五格指标带。
- **强项**：第一眼辨识度最高；把“混合检索 + 重排”讲成关卡，演示友好；像素组件天然适合做 loading / 状态 / 空态。
- **风险**：长时间阅读偏累；像素字在中文正文不可用，只能做标题与数字。
- **适合**：作品集、黑客松、开发者工具、Demo Day。

### B · GROUNDTRUTH — 计量仪器 / 纸质档案

- **一句话**：把问答记录做成一份可归档、可盖章、可复核的证词。
- **视觉**：暖纸 `#f2efe4`、墨黑 `#17140d`、朱红 `#dc3a1b`、档案蓝 `#1e34c0`；Instrument Serif 标题 + Archivo 800 + IBM Plex Mono；纸张噪点、72px 网格、裁切标记、条形码、橡皮章。
- **信息结构**：`Q.01 / A.01` 证词体；右侧 EXHIBIT INDEX 列出 3 条证据与命中分；仪表页有复合分表盘、五通道读数、128 例直方图、最差用例台账。
- **强项**：最可信、最适合企业/合规语境；“评测是下一次改配置的依据”这句话有视觉支撑；打印/导出报告几乎零成本。
- **风险**：个性相对克制；纸质语言用不好会显旧。
- **适合**：企业内训、合规、评估报告、需要“可复现”叙事的场景。

### C · SIGNAL GARDEN — 知识生物圈

- **一句话**：文档是种子，上下文是土壤，评测是花期。
- **视觉**：深绿 `#03100c`、薄荷 `#8dffb8`、荧光黄绿 `#d9ff6a`、珊瑚 `#ff7a6b`；Fraunces 软衬线 + Pixelify Sans 像素数字 + DM Mono；480×300 低分辨率 canvas 山丘、萤火虫、根系 SVG、同心开花环。
- **信息结构**：冠层对话 + 根系追踪（6 条种子路径 + 土壤层）；种子库 9 张物种卡；花期页用五环 + 128 点星座 + 最差花期表。
- **强项**：唯一有完整隐喻的方向，情绪与记忆点最强；适合讲品牌故事。
- **风险**：实现成本最高；数据密集时层级容易被风景稀释；小屏需要重排。
- **适合**：品牌官网、内容型产品、需要“温度”的 AI 产品。

### D · CHROMA//DECK — Y2K 广播台

- **一句话**：把评测直播化——节目监视器、四路多画面、ON AIR、下三分之一字幕条。
- **视觉**：深紫黑 `#06030d`、荧光粉 `#ff3ea5`、青 `#3cf2ff`、紫 `#8b5cff`、荧光绿 `#d9ff3e`；Unbounded 超宽标题 + DM Mono；金属渐变、扫描线、径向网格。
- **信息结构**：PGM 监视器 + 2×2 multiviewer（检索/重排/延迟/信号）+ RUN QUEUE + 底部评分字幕条；资料库是磁带卡 + 播放列表；评分页是黑胶 + 128 格 LED 评分墙。
- **强项**：信息密度最高，最像“正在发生”；大屏演示效果最好；Y2K 视觉在 AI 产品里仍稀缺。
- **风险**：元素多，小屏必须重排；小字较多。
- **适合**：实时监控、Demo Day、数据直播、需要“秀”的发布场景。

---

## 2. 横向对比

| 维度 | A | B | C | D |
|------|---|---|---|---|
| 气质 | 街机 / 开发者 | 实验室 / 审计 | 生物圈 / 叙事 | 广播台 / 秀场 |
| 信息密度 | 中 | 高 | 低-中 | 最高 |
| 动效强度 | 高 | 低 | 中 | 高 |
| 中文排版 | 像素标题 + 等宽正文 | 衬线标题 + 档案正文（最稳） | 软衬线 + 像素数字（最柔） | 超宽标题 + 等宽数据（最潮） |
| 实现成本 | 中 | 低 | 高 | 中高 |
| 最适合 | 作品集 / 黑客松 | 企业 / 合规 | 品牌 / 内容 | 大屏 / 实时 |

**最终选择 A**。落地时借鉴 **B 的信息结构**（证据索引、用例台账、可复核的数字层级），但保留 A 的像素计分牌与检索关卡叙事，不混搭 B 的纸质视觉。

---

## 3. 共享数据契约（四版一致）

原型共用一套 mock，目的是让比较只关于视觉与结构。A 为最终方向，复合分已按 `.45 × retrieval + .55 × generation` 重算为 `0.846`（B/C/D 的归档截图仍保留 `0.839`）：

```json
{
  "index": { "chunks": 48219, "collections": 12, "embedding": "BGE-M3", "dim": 1024 },
  "pipeline": { "bm25": 24, "dense": 24, "rrf_k": 60, "rerank_top": 6, "latency_ms": 27 },
  "answerer": "Qwen2.5-72B",
  "reranker": "bge-reranker-v2-m3",
  "metrics": {
    "hit_rate_at_5": 0.873,
    "mrr": 0.742,
    "context_precision": 0.681,
    "faithfulness": 0.914,
    "answer_relevance": 0.887,
    "composite": 0.846
  },
  "eval": { "set": "Golden-128", "run": 42, "duration": "6m42s", "pass": 119, "warn": 7, "fail": 2 },
  "question": "当 BM25 和向量召回给出相互冲突的证据时，reranker 如何权衡？"
}
```

正式实现时这份契约会变成 API 的 response schema，前端类型从 OpenAPI 生成。

---

## 4. 设计令牌（选定后抽成 Tailwind theme）

### A

```css
--bg:#07070c; --panel:#0d0d15; --line:#232338;
--lime:#c8ff3d; --pink:#ff3d9a; --cyan:#38e8ff; --amber:#ffb020; --violet:#9d7bff;
--fg:#ece9f5; --muted:#8a87a0;
```

### B

```css
--paper:#f2efe4; --paper-2:#e9e4d5; --ink:#17140d; --muted:#6b6555;
--red:#dc3a1b; --blue:#1e34c0; --gold:#a87c12; --rule:#cfc7b2;
```

### C

```css
--void:#03100c; --panel:rgba(6,30,22,.74); --mint:#8dffb8; --lime:#d9ff6a;
--teal:#2ee6c0; --amber:#ffc46b; --coral:#ff7a6b; --fg:#dff7e8; --muted:#7fa994;
```

### D

```css
--bg:#06030d; --panel:rgba(18,10,32,.72); --pink:#ff3ea5; --cyan:#3cf2ff;
--violet:#8b5cff; --lime:#d9ff3e; --fg:#f3e9ff; --muted:#9a86b8;
```

字体：A `Silkscreen + Space Grotesk + IBM Plex Mono`；B `Instrument Serif + Archivo + IBM Plex Mono`；C `Fraunces + Pixelify Sans + DM Mono`；D `Unbounded + DM Mono`。中文统一 `Noto Sans SC`，B 可加 `Noto Serif SC`。

---

## 5. 从原型到 React 的映射

无论选哪版，页面骨架都对应同一组模块，方便解耦：

| 原型区块 | React 组件 | Zustand store | REST |
|----------|------------|---------------|------|
| 对话流 | `<Thread />` `<Message />` | `chatStore` | `POST /api/conversations/:id/messages` |
| 检索追踪 | `<RetrievalTrace />` | `traceStore` | `GET /api/messages/:id/trace` |
| 文档库 | `<CollectionGrid />` | `corpusStore` | `GET /api/collections` `POST /api/ingest` |
| 评测仪表 | `<MetricDeck />` `<RunDetail />` | `evalStore` | `GET /api/eval/runs/:id` `POST /api/eval/runs` |
| 用例表 | `<CaseTable />` | `evalStore` | `GET /api/eval/runs/:id/cases` |
| 运行队列 | `<RunQueue />` | `evalStore`（轮询/SSE） | `GET /api/eval/runs?status=` |

原则：

1. **展示与数据分离**：组件只接 props，容器负责请求；Zustand 只存跨页状态（当前会话、当前 run、过滤器）。
2. **指标计算在后端**：前端不重算 Hit/MRR/CP；Faithfulness 与 Answer Relevance 由后端调 HuggingFace 模型，前端只展示分数与解释。
3. **一条 trace 一条记录**：检索链每一步（rewrite / bm25 / dense / rrf / rerank）都作为 `trace_steps` 行存储，前端按 stage 渲染，换视觉不影响数据。
4. **主题即 tokens**：选定方向后把上面四组变量写进 `tailwind.config` + CSS variables；组件不写死颜色。

后端 REST 草案：

```
POST /api/conversations                 创建会话
POST /api/conversations/{id}/messages   提问，返回 answer + citations + trace
GET  /api/collections                   知识库列表
POST /api/collections/{id}/documents    上传/切分/向量化
GET  /api/eval/sets                     评测集列表
POST /api/eval/runs                     触发评测
GET  /api/eval/runs/{id}                指标 + 用例明细
GET  /api/eval/runs/{id}/cases          分页用例
```

评测指标定义（后端实现）：

- **Hit Rate@K**：top-K 检索结果中是否包含至少一个 ground-truth chunk。
- **MRR**：第一个正确 chunk 的排名倒数，跨用例平均。
- **Context Precision**：被召回且真正相关的 chunk 占 top-K 的比例（可按排名加权）。
- **Faithfulness**：答案中的每个 claim 是否能被 context 支持；HuggingFace NLI/事实一致性模型打分。
- **Answer Relevance**：答案与问题的语义相关度；HuggingFace embedding/相关性模型打分。
- **Composite**：`0.45 × retrieval + 0.55 × generation`，retrieval = Hit/MRR/CP 加权，generation = Faith/AR 加权；权重可在设置页改。

---

## 6. 选型时只看三个问题

1. **谁看？** 面试官/同行 → A 或 D；企业客户/合规 → B；品牌与内容团队 → C。
2. **看多久？** 30 秒演示 → A/D；10 分钟阅读报告 → B；长时间陪伴 → C。
3. **下一步要加什么？** 实时监控/大屏 → D；导出 PDF 报告 → B；上传与知识治理 → A/B；内容运营 → C。

已选定 A，接下来：

1. 把 A 的 tokens 与组件拆进 `apps/web`（React + Zustand + shadcn/ui + Tailwind + axios）；
2. 搭 `apps/api`（FastAPI + PostgreSQL + 混合检索 + 重排 + 评测任务）；
3. 先打通一条真实链路：上传 → 切分 → 向量化 → 提问 → trace → 评测 run → 分数与用例表；
4. 再补第二、第三个视图，避免一次做完四个空壳。

---

## 7. 文件索引

```
design/
  index.html              四版对比 / 选择页
  concept-a.html          KERNEL ARCADE
  concept-b.html          GROUNDTRUTH
  concept-c.html          SIGNAL GARDEN
  concept-d.html          CHROMA//DECK
  shoot.ps1               Edge headless 截图脚本
  DESIGN-NOTES.md         本文件
  screenshots/
    a-desktop-2.png  a-eval.png  a-corpus.png
    b-transcript.png b-specimens.png b-instrument.png
    c-canopy.png     c-bloom.png     c-vault.png
    d-broadcast.png  d-library.png   d-ratings.png
    gallery.png      gallery-full.png
```
