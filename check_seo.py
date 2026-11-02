# -*- coding: utf-8 -*-
"""SEO-аудит всех страниц из sitemap.xml по локальным файлам: lang, title, description, canonical (на себя), hreflang,
Open Graph, JSON-LD, robots. Печатает сводку по типам страниц и все отклонения.
Запуск: py -3.12 check_seo.py"""
import collections
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://aii-crm.com/"


def local(url: str) -> str:
    rel = url[len(BASE):]
    p = os.path.join(HERE, *rel.split("/")) if rel else HERE
    return os.path.join(p, "index.html") if rel.endswith("/") or not rel else p


def kind(url: str) -> str:
    rel = url[len(BASE):]
    if re.fullmatch(r"([a-z]{2}/)?", rel):
        return "home"
    if rel.startswith("guides/") and (rel.endswith("/") or rel == "guides/"):
        return "guides-index"
    if rel.startswith("guides/"):
        return "guide"
    if rel.startswith("cases/"):
        return "cases"
    return "policy"


def meta(h: str, attr: str, name: str):
    m = re.search(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)"', h)
    return m.group(1) if m else None


def main() -> int:
    urls = re.findall(r"<loc>([^<]+)</loc>", io.open(os.path.join(HERE, "sitemap.xml"), encoding="utf-8").read())
    issues, stats = [], collections.defaultdict(collections.Counter)
    for u in urls:
        fp = local(u)
        k = kind(u)
        if not os.path.exists(fp):
            issues.append((u, "file missing"))
            continue
        h = io.open(fp, encoding="utf-8").read()
        head = h[:h.find("</head>")]
        st = stats[k]
        st["pages"] += 1
        lang = re.search(r'<html lang="([^"]+)"', h)
        title = re.search(r"<title>(.*?)</title>", head, re.S)
        desc = meta(head, "name", "description")
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', head)
        hl = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', head)
        robots = meta(head, "name", "robots") or ""
        lds = []
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                o = json.loads(m.group(1))
            except ValueError:
                issues.append((u, "JSON-LD does not parse"))
                continue
            for x in (o.get("@graph") or [o]):
                lds.append(x.get("@type"))
        for name, ok in (("lang", bool(lang)), ("title", bool(title and title.group(1).strip())), ("description", bool(desc)),
                         ("canonical", bool(canon)), ("og:title", bool(meta(head, "property", "og:title"))),
                         ("og:description", bool(meta(head, "property", "og:description"))), ("og:locale", bool(meta(head, "property", "og:locale"))),
                         ("og:image", bool(meta(head, "property", "og:image"))), ("json-ld", bool(lds))):
            st[name] += ok
        if canon and canon.group(1) != u:
            issues.append((u, f"canonical → {canon.group(1)}"))
        if "noindex" in robots:
            issues.append((u, "noindex"))
        if len(hl) != 13:
            issues.append((u, f"hreflang {len(hl)}"))
        elif u not in [x[1] for x in hl]:
            issues.append((u, "hreflang set does not include the page itself"))
        if title and len(title.group(1)) > 75:
            st["title>75"] += 1
        if desc and len(desc) > 170:
            st["desc>170"] += 1
        for t in lds:
            st["ld:" + str(t)] += 1
    print(f"{len(urls)} URLs in sitemap\n")
    for k, st in stats.items():
        n = st.pop("pages")
        print(f"{k}: {n} pages")
        print("   " + ", ".join(f"{name} {v}/{n}" if not name.startswith(("ld:", "title>", "desc>")) else f"{name} {v}" for name, v in st.items()))
    print(f"\nissues: {len(issues)}")
    for u, msg in issues[:40]:
        print(f"  {u[len(BASE):] or '/'}: {msg}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
