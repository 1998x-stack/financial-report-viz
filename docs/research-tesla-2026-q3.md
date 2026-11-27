# Tesla 2026 Q3 · Source audit and research notes

## Primary evidence / data boundary

- **Issuer**: Tesla, Inc. (NASDAQ: TSLA), consolidated U.S. GAAP, quarterly interim information **unaudited**.
- **Quarter**: 2026-07-01 to 2026-09-30; equal-length comparator 2025-07-01 to 2025-09-30.
- **Original issuer PDF**: [Tesla Q3 2026 Update (33 pages)](https://assets-ir.tesla.com/tesla-contents/IR/TSLA-Q3-2026-Update.pdf), dated 2026-10-21; PDF viewer page = printed page.
- **SEC cross-check**: [2026-09-30 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026066775/tsla-20260930.htm), accepted 2026-10-21.
- **Original currency and units**: statement of operations, financial summaries and balance sheet in **USD millions**; operational data have independently labeled cars, GWh, million active subscriptions, stations, etc. No normalization into RMB and no invented zeroes for missing disclosures.
- **Source page locators**: p.4 financial summary; p.5 operations; p.25 management commentary; p.27 income statement; p.28 balance sheet; p.29 cash-flow statement; p.30 GAAP/non-GAAP; p.31 quarterly cash/EBITDA details.

## Reported → calculated → interpreted: keep distinct

| Question | Exact source evidence | Reconciliation / limit |
| --- | --- | --- |
| Why is revenue flat? | Q3'25 28,095; Q3'26 28,046. Auto: 21,205→20,560; energy: 3,415→2,881; services: 3,475→4,605 (p.27). | −645−534+1,130=−49 USDm; YoY −0.17%. Reported segment amounts; calculated bridge. |
| Why does profit fall despite gross recovery? | Gross 5,054→5,494; operating expenses 3,430→4,776; operating income 1,624→718 (p.27). | Gross delta +440 offset by operating expense delta +1,346 = operating income delta −906 USDm. 2026 Q3 gross 5,494 − R&D 2,761 − SG&A 2,015 = operating profit 718. |
| How does GAAP reconcile to non-GAAP? | GAAP attributable 787; SBC net-tax +982; digital asset net-tax −224; SpaceX unrealized net-tax +108; certain tax items +44; Non-GAAP 1,697 (p.30). | 787+982−224+108+44=1,697 USDm. Does **not** mean FCF or EBITDA. |
| Where did free cash go? | OCF 6,263; capex 4,732; FCF 1,531 (pp.4,29/31). | 6,263−4,732=1,531. The capital expenditure number is treated as absolute spend in figures; signed negative in cash flow statement. |
| Did vehicle demand accelerate? | Production 464,391 vs 447,450; deliveries 486,532 vs 497,099 (p.5). | Production +3.8%; deliveries −2.1%. Volume does not establish ASP, profit or product-market fit. |
| Is energy a growth engine this quarter? | Storage deployed 13.7GWh vs 12.5GWh (p.5); energy revenue 2,881 vs 3,415 USDm (p.27). | Deployment +9.6% vs revenue −15.6%; recognizes timing/product mix and management's tariff-related-refund commentary, not a unit economic estimate. |
| Is subscription growth monetizing? | Active FSD subscriptions 1.74m vs 1.04m (p.5). | +67.3%; includes upfront purchases, excludes free trials, not directly an ARR disclosure. |

## Management commentary / third-party evaluation

The 2026 Q3 issuer update p.25 attributes the flat revenue to lower vehicle ASP, regulatory credits, deliveries and energy, offset by services and FX. Lower operating income reflects SI-related R&D and SG&A increases, offset by favorable vehicle mix. **These are management attributions**, not independently established causal estimates.

In the [SEC 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026066775/tsla-20260930.htm), Tesla says it expects *in excess of $20 billion* in 2026 capex for SI compute, factories, and asset growth, with possible external funding needs in high-capex phases. Forward-looking, not an amount already spent.

Tesla posted [company-compiled sell-side consensus on 2026-10-19](https://ir.tesla.com/press-release/earnings-consensus-third-quarter-2026): mean revenue 28,341 vs actual 28,046 USDm; mean operating income 721 vs actual 718; mean capital expenditure 7,771 vs actual 4,732; mean FCF −4,506 vs actual +1,531. These are a dated *pre-release* opinion sample, not financial statement data, and Tesla did not endorse them.

[Reuters, 2026-10-22](https://www.reuters.com/business/autos-transportation/tesla-drops-spending-pullback-clouds-ai-robotics-ambitions-2026-10-22/) examined how a lower capex target could be read either as better liquidity discipline or slower AI/robotics investments. Treat as journalistic external commentary, not confirmed business value.

## Limitations

- No current stock price, EV/EBITDA, valuation, forward price target, peer comparisons, or unsourced Robotaxi unit economics are included.
- One-off recognition, geography mix, and management guidance may affect comparability; sector totals are GAAP revenue, not cash inflows.
- Capital expenditure is a flow; cash/investments, liabilities and inventory are end-of-quarter balance-sheet stocks; do not add them together.
- Operational subscriptions and GWh are original-unit readings. FSD subscriptions include paid upfront and monthly and exclude free trials per the quarterly update.
- Q3 2026 SEC and issuer statements are **unaudited**, not merely assumed audited by virtue of SEC filing.
- Original PDF is linked, not mirrored. All SVG artwork and charts in this repository are original and generated from transcribed figures.
