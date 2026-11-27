#!/usr/bin/env python3
"""Real local/offline Chromium QA. Requires Playwright and installed Chromium."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"


def run():
    from playwright.sync_api import sync_playwright
    targets=[("index.html",None),
             ("reports/index.html","report-search"),
             ("reports/xindong/2026-h1/index.html","metric-search"),
             ("reports/tencent/2026-q3/index.html","tencent-metric-search"),
             ("concepts/index.html","concept-search"),
             ("concepts/accounting-equation/index.html","concept-detail"),
             ("concepts/pe-ratio/index.html","concept-detail")]
    sizes=[(1440,900),(768,1024),(390,844),(360,800)]
    output=ROOT/"reports"/"browser"
    output.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            for relative,search in targets:
                for width,height in sizes:
                    ctx=browser.new_context(
                        viewport={"width":width,"height":height},
                        accept_downloads=True,
                        reduced_motion="reduce")
                    ctx.set_offline(True)
                    page=ctx.new_page()
                    issues=[]
                    page.on("pageerror",lambda err:issues.append(str(err)))
                    page.on("console",lambda msg:issues.append(msg.text)
                            if msg.type=="error" else None)
                    page.goto((DIST/relative).as_uri(),wait_until="load")
                    page.locator("main h1").wait_for()
                    page.locator("img").evaluate_all("(imgs) => imgs.forEach(img => img.loading = 'eager')")
                    page.wait_for_function("Array.from(document.images).every(img => img.complete)", timeout=15000)
                    overflow=page.evaluate(
                        "()=>document.documentElement.scrollWidth-window.innerWidth")
                    if overflow>2:issues.append("horizontal document overflow: "+str(overflow))
                    bad_images=page.locator("img").evaluate_all(
                        "els=>els.filter(e=>!e.complete||e.naturalWidth<=0).map(e=>e.src)")
                    if bad_images:issues.append("unloaded images: "+str(bad_images))
                    if search and width==1440:
                        if search=="report-search":
                            page.locator("#report-search").fill("not-exists-anywhere")
                            visible=page.locator("[data-filter-container] [data-search]:visible").count()
                            if visible!=0:issues.append("archive filtering did not hide all cards")
                            page.locator("#report-search").fill("心动")
                            if page.locator("[data-filter-container] [data-search]:visible").count()!=1:
                                issues.append("archive filtering did not restore matching card")
                        elif search=="concept-search":
                            cards=page.locator("[data-glossary-card]")
                            if cards.count()!=100:issues.append("concept index must show exactly 100 cards")
                            page.locator("#concept-search").fill("ROE")
                            n=page.locator("[data-glossary-card]:visible").count()
                            if n<1:issues.append("concept search missing ROE")
                            page.locator("#concept-search").fill("")
                            page.locator('[data-glossary-filter="cash"]').click()
                            n=page.locator("[data-glossary-card]:visible").count()
                            if n!=10:issues.append("cash chapter filter expected ten terms, got "+str(n))
                            page.locator('[data-glossary-filter="all"]').click()
                        elif search=="concept-detail":
                            if page.locator(".glossary-figure img").count()!=1:
                                issues.append("missing concept visual SVG")
                            if page.locator(".glossary-equation").count()!=1:
                                issues.append("concept formula missing")
                            if page.locator(".glossary-related-card").count()<2:
                                issues.append("concept related links missing")
                        else:
                            term="资本开支" if search=="tencent-metric-search" else "研发"
                            page.locator("#metric-search").fill(term)
                            count=page.locator("[data-metric-row]:visible").count()
                            if count!=1:issues.append("metric search returned "+str(count))
                            page.locator("#metric-search").fill("")
                            if page.locator(".figure-card img").count()<8:
                                issues.append("missing expected figure count")
                            with page.expect_download() as event:
                                page.locator("[data-download-table]").click()
                            dl=event.value
                            if not dl.suggested_filename.endswith(".csv"):
                                issues.append("CSV download filename invalid")
                            dl.save_as(output/("financial-metrics-tencent.csv" if search=="tencent-metric-search" else "financial-metrics-xindong.csv"))
                            page.emulate_media(media="print")
                    filename=relative.replace("/","_").replace(".html","")
                    page.screenshot(path=str(output/f"{filename}-{width}.png"),full_page=False)
                    results.append(dict(page=relative,width=width,
                                        overflow=max(0,overflow),
                                        image_count=page.locator("img").count(),
                                        status="pass" if not issues else "fail",
                                        errors=issues))
                    if issues:raise RuntimeError(f"{relative}@{width}: {issues}")
                    ctx.close()
        finally:
            browser.close()
    (output/"report.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),
                                      encoding="utf-8")
    print("PASS: Chromium offline viewports, figures, search, CSV and print")
    return 0


if __name__=="__main__":
    try:raise SystemExit(run())
    except Exception as exc:
        print("FAIL:",exc,file=sys.stderr)
        raise SystemExit(1)
