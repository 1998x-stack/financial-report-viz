#!/usr/bin/env python3
"""Inspect generated static pages, in-repository links, JSON-LD and standalone SVGs."""
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"


class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.h1=0
        self.titles=0
        self.images=[]
        self.canonical=0
        self.script_json=False
        self.json_chunks=[]
        self._json_data=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="h1":self.h1+=1
        if tag=="title":self.titles+=1
        if tag=="link" and a.get("rel")=="canonical":self.canonical+=1
        if tag in ("a","link","script","img"):
            u=a.get("href") if tag in ("a","link") else a.get("src")
            if u:self.links.append(u)
        if tag=="img":self.images.append(a)
        if tag=="script" and a.get("type")=="application/ld+json":
            self.script_json=True;self._json_data=[]
    def handle_data(self,data):
        if self.script_json:self._json_data.append(data)
    def handle_endtag(self,tag):
        if tag=="script" and self.script_json:
            self.json_chunks.append("".join(self._json_data))
            self.script_json=False


def check():
    errors=[]
    if not DIST.exists():return ["missing dist/; run build_site.py first"]
    htmls=sorted(DIST.rglob("*.html"))
    if len(htmls)<5:errors.append("expected 5+ distinct site HTML pages")
    for file in htmls:
        parser=PageInspector()
        try:
            parser.feed(file.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(str(file)+": HTML parse: "+str(exc));continue
        if parser.h1!=1:errors.append(str(file)+f": expected exactly one H1, got {parser.h1}")
        if parser.titles!=1:errors.append(str(file)+": expected one <title>")
        if parser.canonical!=1:errors.append(str(file)+": expected canonical URL")
        for u in parser.links:
            url=urlsplit(u)
            if url.scheme in ("https","http","mailto","tel") or u.startswith("//"):
                continue
            if url.scheme or not url.path:
                continue
            target=(file.parent/unquote(url.path)).resolve()
            if DIST.resolve() not in target.parents and target!=DIST.resolve():
                errors.append(str(file)+": link escapes dist: "+u)
            elif not target.exists():
                errors.append(str(file)+": broken local asset/link: "+u)
        for im in parser.images:
            if not im.get("alt"):
                errors.append(str(file)+": missing image alternative description")
        for fragment in parser.json_chunks:
            try:
                j=json.loads(fragment)
                if not j.get("@context"):
                    errors.append(str(file)+": JSON-LD lacks @context")
            except ValueError:
                errors.append(str(file)+": invalid JSON-LD")
    svgs=sorted(DIST.rglob("*.svg"))
    if len(svgs)<8:errors.append("expected eight original SVG figures in first report")
    for file in svgs:
        try:
            node=ET.parse(file).getroot()
            if "viewBox" not in node.attrib:errors.append(str(file)+": missing viewBox")
            titles=[a for a in node.iter() if a.tag.endswith("title")]
            descs=[a for a in node.iter() if a.tag.endswith("desc")]
            if not titles or not descs:errors.append(str(file)+": missing title/desc")
            content=file.read_text(encoding="utf-8")
            if re.search(r"(?:https?://|<script|foreignObject)",content,re.I):
                errors.append(str(file)+": external resource or unsafe markup")
        except ET.ParseError as exc:
            errors.append(str(file)+": SVG invalid XML: "+str(exc))
    try:
        catalog=json.loads((DIST/"catalog.json").read_text(encoding="utf-8"))
        if not catalog["reports"]:errors.append("catalog must contain published reports")
        for r in catalog["reports"]:
            if not r["source_url"].startswith("https://"):
                errors.append("catalog missing authoritative PDF link: "+r["report_id"])
    except Exception as exc:
        errors.append("catalog JSON: "+str(exc))
    return errors


if __name__=="__main__":
    issues=check()
    if issues:
        for issue in issues:print("ERROR:",issue,file=sys.stderr)
        raise SystemExit(1)
    print("PASS: local links, metadata, source catalog, accessible SVGs and site structure")
