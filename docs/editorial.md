# Editorial and category policy

## Public information architecture

1. **Home**: editorial headline, latest reports and browse by sector/market/topic. Latest means latest **available in this catalog**, not latest filed by issuer.
2. **Reports** `/reports/`: searchable archive (date descending, issuer, period, sector).
3. **Issuer** `/companies/<issuer-id>/`: stable company profile and timeline.
4. **Report** `/reports/<issuer-id>/<yyyy>-<period>/`: one canonical permalink. Recommended blocks: context / KPI / growth / segment driver / profit reconciliation / cash flow / user activity where available / financial table / source and notes.
5. **Category** `/categories/<kind>/<slug>/`: registry-driven index; only create when reports exist.
6. **Machine-readable** `/catalog.json`, `/sitemap.xml`, `/robots.txt`; report JSON-LD `Article` with `citation` and `about` when grounded.

## Editorial taxonomy design

Use **orthogonal dimensions**, never one giant ambiguous category tree.

- `sector`: e.g. `gaming-digital-platforms` (a stable primary segment). One primary per issuer, update only with evidence.
- `market`: e.g. `hkex`, `sse`, `szse`, `nasdaq`; issuer-level listing.
- `period`: `fy`, `h1`, `q1`, `q3`, `q4` as appropriate. Do not treat H1 as FY or standalone Q2.
- `topics`: editorial facets `growth`, `profitability`, `segments`, `cash-flow`, `users`, `valuation`, etc. Include only topics actually supported by the report.
- `locale`: `zh-CN` initially; language is independent of listing market.

URLs use ASCII slugs and remain stable. Avoid year-specific hardcoded menus: archive and category pages are generated from the corpus.

## Statement and chart contract

- Save exact positive values for expenses in `values` plus `sign_convention: expenses_positive`; bridge renderer subtracts them explicitly.
- Numeric `reported` values are integers **RMB thousand** in the Xindong example; only presentational conversion to 亿元 divides by 100000.
- Each material metric has a `page` and `kind`, and all evidence must point to primary PDF; financial statements take precedence over rounded summary prose.
- `derived` YoY, margin and percentage points are calculated from normalized inputs in the builder, never transcribed as independent truth.
- Source PDF may include pages with a cover offset. `page` records *printed page number*, links use the viewer page offset documented in the report (`pdf_page_offset`).
- Cash and balances are point-in-time; flow/earnings are six-month intervals. Never place incompatible periods on one time-series without explicit label.
- IFRS profit and company's adjusted/non-IFRS profit are categorically separate.
- TTM, share price, PE and market cap require dated external market sources and are not inferred from this PDF.

## Release checklist

Check there are no empty links, broken relative paths, off-page SVG labels, inaccessible controls or missing citations. Verify desktop/mobile/print/offline. Review the screenshot next to source PDF page before merging. CI only confirms what it truly executed.
