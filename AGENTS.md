# AGENTS.md — Financial Report Atlas

> This repository is a permanent, growing publication of evidence-backed visual financial reports. Its audience may treat figures as investment-relevant. **Source accuracy and accounting comparability override visual polish or speed.**

## Authority, priority and skills

1. The original issuer filing, with exact version, printed page, period, currency, accounting scope and audit/review status, is the primary source of reported figures.
2. Local `data/reports/*/*.json` is a **versioned transcription**, never a substitute for the PDF. Resolve disagreements against the disclosure and record the correction.
3. Follow [Financial-Visualization SKILL](https://github.com/1998x-stack/Financial-Visualization/blob/main/skills/financial-visualization/SKILL.md) for evidence-first eight-gate workflow, choice of 16 chart types, SVG/render checks, numerical validation and browser QA.
4. Read `docs/editorial.md`, `docs/data-model.md` and `schemas/report.schema.json` before writing a new report.

## Site architecture and ownership

- `data/taxonomy.json`: single authoritative stable IDs for markets, sectors, period types and editorial topics.
- `data/issuers/<issuer-id>.json`: company-level identity; ticker, exchange, country, sector. Do not repeat company metadata in each report.
- `data/reports/<issuer-id>/<yyyy>-<period>.json`: one immutable canonical identifier per issuer/reporting period; all reported metrics in **original source unit**, with provenance.
- `schemas/`: machine-readable JSON Schemas; version intentionally.
- `src/templates/`: site HTML structure; page types home, listing, issuer, topic/market and report.
- `src/static/`: shared CSS/JS only; never insert per-company financial copy here.
- `src/charts.py`: original standalone vector diagrams generated from validated report data.
- `scripts/`: deterministic build/validation, HTML and browser QA.
- `dist/`: generated publish artifact. NEVER hand-edit; regenerated on CI.
- `docs/`: contributor workflow, taxonomy rules and architecture decisions.

## Mandatory publishing gates

**0 — Source:** Open original PDF, inspect key statement pages as actual page images, record source URL, printed page numbers, issuer, publication/approval date only if explicit. A report is not audited merely because an auditor performed an interim review.

**1 — Transcription:** Key `values` remain the disclosed RMB thousand etc. Use `null` if missing. Never silently substitute estimates, infer geography, market data, adjusted profit or business drivers.

**2 — Reconciliation:** For this issuer, revenue - cost = gross profit; segment game + TapTap = total revenue; 2026 H1 operating-profit and net-profit bridges match reported statement; cash-flow totals reconcile when all relevant components exist. Use exact integers before rounding. Periods of different length are not compared YoY.

**3 — Narrative:** Write a question per chart. Separate *reported fact*, *derived ratio*, *management's explanation*, *analyst interpretation*, and *unknown*. Cite source pages near every table/chart. If a causal driver is management commentary, attribute it as such.

**4 — Visual:** Choose only diagrams that help understanding (from 16-chart catalog). Standard amount bars begin at 0; all units and denominator definitions visible; `pp` is not `%`. For Sankey/waterfalls verify flow conservation; do not confuse profit flow with actual cash. Visually distinct estimates (not used in this release).

**5 — Accessible presentation:** Semantic landmarks, one H1/page, meaningful SVG title/desc, non-color labels, responsive 360/390/768/1440 px, visible focus, reduced motion, high contrast, printer-friendly sources. No external font/CDN dependency for core content.

**6 — Tests:** `python scripts/validate_data.py`, `python -m unittest discover -s tests -v`, `python scripts/build_site.py`, `python scripts/check_site.py`, and, if Chromium present, `python scripts/browser_qa.py`. Failed checks block publication; report skipped checks as not verified.

**7 — Review and release:** Use a feature branch + PR. Confirm CI success and inspect the diff before merging. Deploy generated `dist/` only, with Pages workflow. Check actual remote deployment status before saying the site is live.

## Adding a new report

1. Create issuer JSON only if company ID does not exist.
2. Add `data/reports/<issuer-id>/<year>-<period>.json`; do not modify old reporting periods to reuse a filename.
3. Ensure `report_id` unique, full sources for material metrics, consistent periods and `status` (`draft` or `published`).
4. Use taxonomy IDs from the registry. New taxonomy only by editing registry and describing definition/overlap.
5. Run all tests. Preview every new chart and source anchor manually. Publish via PR, never by editing generated files.
6. If a filing restates prior figures, preserve original report and add restatement/version annotations rather than silently replacing history.

## Hard blocks

- Never invent numbers, consensus forecasts, fiscal dates, actual stock prices, percentages, sources or page references.
- Do not mislabel reviewed-but-unaudited financials as audited.
- Do not claim all 16 chart forms are present unless 16 independent forms are actually built.
- Never claim GitHub Pages/CI is deployed unless checked.
- No unrelated third-party artwork or unlicensed code/fonts.
- Do not embed production process notes in public research article hero; put such notes in docs.
- Use only source-derived operational data and attributed management commentary; no unsupported causal statements.

## Commands

```bash
python scripts/validate_data.py
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/check_site.py
python scripts/browser_qa.py  # optional, requires playwright and Chromium
python -m http.server 8000 -d dist
```
