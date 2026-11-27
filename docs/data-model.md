# Data model and onboarding

## Canonical entities

- `issuer`: `id`, legal/short names, ticker, exchange, sector, country and listing link.
- `report`: `report_id`, `issuer_id`, `year`, `period_type`, fiscal start/end and exact comparable start/end, source URL, primary-source printed page offset, assurance status, accounting basis, currency/unit, topic IDs, narrative and metric dictionary.
- `metric`: stable English snake_case key, Chinese human label, 2 period values under `prior` and `current`, source printed page, and `kind: reported`. No forecast values in a reported-only chart.
- `taxonomy`: registry of `sectors`, `markets`, `periods`, `topics` with stable slugs.

## Naming and paths

```text
data/issuers/xindong.json
data/reports/xindong/2026-h1.json
schemas/{issuer,report}.schema.json
src/templates/{base,home,listing,issuer,report}.html
src/static/{site.css,site.js}
src/charts.py
scripts/{validate_data,build_site,check_site,browser_qa}.py
tests/
dist/                  # generated only
```

Report ID is `<issuer-id>-<yyyy>-<period>`; detail URL is `/reports/<issuer-id>/<yyyy>-<period>/`. A reporting-period slug is not the filing publication date. Distinguish IAS34 interim review from annual audit.

## Extensibility rules

New company => one issuer JSON. New earnings => one report JSON. Add only verified metrics that support the report; chart renderer checks availability. Add additional company-specific modules under `src/` rather than copy-pasting 16 individual HTML pages.

To add a facet, extend `data/taxonomy.json` with a **stable ID**, title and description; use in report JSON and rebuild. Previous URLs must remain stable. Migration/relabeling requires redirect/alias and documentation.

Every report has an unambiguous primary PDF; do not store third-party PDF bytes in the public repo unless redistribution permitted. Keep pages and source URLs in data. A typed `Article` JSON-LD fragment is emitted only for published articles.

## Grounded first report

Xindong Limited 2026 H1 original source is a 110-page document:
https://img.xdcdn.net/xdwp/2026/10/20261009091224167.pdf

Primary figures: financial highlights printed p.5; segment revenue p.9 and notes pp.68-69; consolidated income p.49; operating cash p.58; operation users p.5; geography p.70. Reporting basis: IFRS/IAS 34, reviewed interim financial information (unaudited). Board approval/reviewer date August 28, 2026 (pp.47,53), **not asserted as publication date**.

No fictitious peer, valuation band, price, revenue forecasts or company's unpublished user data should be added.