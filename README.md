# Financial Report Atlas · 财报可视化资料库

**从上市公司原始披露，到可核验的图表研究。** 本项目是一个持续增长的财报网站，而不是逐篇复制 HTML 的单次展示。公司档案、行业/上市市场/主题分类、报告文章、原始指标表、SVG 图形与 SEO 页面均由数据自动构建。

## 访问与来源

- GitHub Pages（启用且部署成功后）：https://1998x-stack.github.io/financial-report-viz/
- GitHub 仓库：https://github.com/1998x-stack/financial-report-viz
- 基础方法论：[Financial-Visualization SKILL](https://github.com/1998x-stack/Financial-Visualization/blob/main/skills/financial-visualization/SKILL.md)
- 核心 Agent 规范：[AGENTS.md](AGENTS.md)
- 当前第一篇：心动有限公司（2400.HK）《2026年中期报告》，源 PDF：https://img.xdcdn.net/xdwp/2026/10/20261009091224167.pdf

## 信息架构

| 页面 | 路径 | 作用 |
|---|---|---|
| 首页 | `/` | 最新已收录研究、归档统计、分类导航 |
| 所有财报 | `/reports/` | 搜索、浏览全部已发布报告 |
| 公司目录 | `/companies/` | 所有已覆盖发行人的入口 |
| 公司档案 | `/companies/<issuer-id>/` | 发行人详情、报告时间线 |
| 财报文章 | `/reports/<issuer-id>/<yyyy>-<period>/` | KPI、经营解读、SVG、数据表及来源 |
| 细分分类 | `/categories/<kind>/<id>/` | 行业、市场、期间、主题四个维度 |
| 程序目录 | `/catalog.json` | 全站可检索的结构化内容索引 |

分类是独立正交维度，不将市场、行业与研究主题混成一条树。稳定 ID 与描述维护于 `data/taxonomy.json`。公司、报告各有独立 canonical ID；URL 不随发布日期变化。

## 目录布局

```text
.
├── AGENTS.md                         # Agent 执行契约与发布红线
├── docs/
│   ├── editorial.md                  # 分类、文案、图表和质量准则
│   └── data-model.md                 # 数据结构和新增报告流程
├── data/
│   ├── taxonomy.json                 # 稳定行业/市场/期间/主题 IDs
│   ├── issuers/xindong.json          # 发行人元信息
│   └── reports/xindong/2026-h1.json  # 披露数字、来源页码、审阅状态
├── schemas/
│   ├── issuer.schema.json
│   └── report.schema.json
├── src/
│   ├── templates/                    # 首页、归档、公司、财报文章
│   ├── static/                       # 统一 CSS 和浏览器增强功能
│   └── charts.py                     # 源驱动原生 SVG
├── scripts/
│   ├── validate_data.py
│   ├── build_site.py
│   ├── check_site.py
│   └── browser_qa.py
├── tests/
├── .github/workflows/site.yml        # CI/Pages
└── dist/                             # 全部由构建脚本生成，不直接编辑
```

## 本地运行与验证

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_data.py
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/check_site.py
python -m playwright install chromium
python scripts/browser_qa.py
python -m http.server 8000 -d dist
```

在浏览器打开 http://localhost:8000/。网站正文和 SVG 可离线阅读，不依赖在线图表 CDN。GitHub Actions 在合并前运行源数据、数值勾稽、HTML/SVG、移动端和离线 QA，`main` 上的成功构建触发 GitHub Pages 发布。

## 如何新增财报

1. 对尚未覆盖的公司，新建一次 `data/issuers/<issuer-id>.json`。
2. 新建 `data/reports/<issuer-id>/<yyyy>-<period>.json`，依据 JSON Schema 填写报告期、原文、审计/审阅状态、每个指标的精确值及来源页。
3. 只使用 `data/taxonomy.json` 中有定义的分类 ID，特殊类别先补登记表和说明。
4. 沿用 Financial-Visualization 的取证、会计勾稽、叙事、SVG、表格和 QA 门槛；不要把同比值、归母利润、调整后利润混为一谈。
5. 执行上面全部检查，审阅差异并通过 PR 发布。不得直接编辑 `dist/` 或绕过来源核对。

## 第一篇报告的边界

心动公司 2026 H1 是 IFRS/IAS 34 经审阅、未经审计的中期信息。收入 33.12 亿元、期内利润 7.24 亿元（同比 +7.5%/-10.6%），提供八张基于披露数据的原创独立 SVG：规模、分部、利润率、详细利润桥、费用、现金流、用户、地区。保留 39 条原始关键指标、来源 PDF 页码、比较期及导出 CSV。未制作缺乏价格来源的 PE/股价图，也不填充伪造的竞争对手数据。

设计和绘图方法参考 Financial-Visualization，但本项目独立编写模板、CSS 和图表。本站数据来自公开发行人报告，本站不镜像源 PDF；研究图解不构成投资建议。


## 新增模块：财报概念图鉴 100 + 1

图鉴首页：https://1998x-stack.github.io/financial-report-viz/concepts/

- 会计等式：https://1998x-stack.github.io/financial-report-viz/concepts/accounting-equation/
- 毛利率：https://1998x-stack.github.io/financial-report-viz/concepts/gross-margin/
- ROE：https://1998x-stack.github.io/financial-report-viz/concepts/roe/
- 市盈率：https://1998x-stack.github.io/financial-report-viz/concepts/pe-ratio/

这是一份人工策划的核心 100 概念学习顺序，而非经过统计的金融关键词词频排名。按10个章节展开，每个概念包含中英术语、定义、原生SVG、核心公式、合成数字示例、常见误区、关联导航和独立可分享页面。新增 **100个概念详情HTML + 1个索引HTML**，不覆盖现有财报研究。

| 路径 | 说明 |
|---|---|
| data/concepts.json | 100 概念的统一内容来源（含教学数字） |
| schemas/concepts.schema.json | 机器可检验数据契约 |
| src/concepts.py | 101 静态页面编译器与八类独立 SVG 生成器 |
| src/templates/concept-index.html | 分类、搜索、图鉴总览页 |
| src/templates/concept-detail.html | 单概念详细图解页 |
| src/static/concepts.css, concepts.js | 视觉设计、搜索与分类交互 |
| scripts/validate_concepts.py | 校验数量、分类、勾稽、零分母 |
| tests/test_concepts.py | 100图形可访问性、数值回归测试 |
| docs/concepts.md | 概念编写、未来扩展和 Agent 边界规范 |

验证：

```bash
python scripts/validate_concepts.py
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/check_site.py
python scripts/browser_qa.py
```

所有示例金额、价格、股数均为人工合成的教学案例，不代表发行人公开披露或实时行情。真实财务指标仍需依据原始报表与附注逐项核实。
