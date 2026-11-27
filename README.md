# Financial Report Atlas / 财报研究资料库

面向持续收录的公开上市公司财报可视化站点。采用规范化 JSON、可溯源披露数据、原生 HTML/SVG、GitHub Pages 静态发布。

首次收录：心动有限公司 (HKEX: 2400)《2026 年中期报告》。

技术规范和 Agent 工作流见 `AGENTS.md`，按 `Financial-Visualization` SKILL 的八道门执行。网站由 `python scripts/build_site.py` 构建到 `dist/`。所有财务数字来自原始 PDF 的指定页码，未经审计中期数据不可称为审计报表。
