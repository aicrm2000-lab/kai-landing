# -*- coding: utf-8 -*-
"""Проверка внутренних ссылок сайта: все href/src, URL в meta content, JSON-LD и sitemap, ведущие на aii-crm.com или
относительные, должны указывать на существующий файл репозитория (каталог → index.html). Внешние ссылки не проверяются.
Запуск: py -3.12 check_links.py   → список битых ссылок, код выхода 1, если они есть."""
import io
import os
import re
import sys
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
HOSTS = {"aii-crm.com", "www.aii-crm.com"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", "i18n", "og", "email"}
HREF_RE = re.compile(r"""\b(?:href|src)=["']([^"']+)["']""")
CONTENT_RE = re.compile(r"""\bcontent=["'](https?://[^"']+|/[^"']*)["']""")
LD_RE = re.compile(r'"(?:url|item|mainEntityOfPage|@id)":\s*"(https://aii-crm\.com/[^"#]*)')
LOC_RE = re.compile(r"<loc>([^<]+)</loc>")


def target_path(url: str, base_dir: str):
    u = urlsplit(url)
    if u.scheme in ("mailto", "tel", "data", "javascript") or url.startswith("#"):
        return None
    if u.scheme:
        if u.netloc not in HOSTS:
            return None
        rel = u.path.lstrip("/")
        p = os.path.join(HERE, *rel.split("/")) if rel else HERE
    elif url.startswith("/"):
        p = os.path.join(HERE, *u.path.lstrip("/").split("/"))
    else:
        if not u.path:
            return None
        p = os.path.normpath(os.path.join(base_dir, *u.path.split("/")))
    if os.path.isdir(p):
        p = os.path.join(p, "index.html")
    return p


def main() -> int:
    broken, checked, files = [], 0, 0
    for root, dirs, names in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if not n.endswith((".html", ".xml")):
                continue
            fp = os.path.join(root, n)
            files += 1
            s = io.open(fp, encoding="utf-8").read()
            urls = set(HREF_RE.findall(s)) | set(CONTENT_RE.findall(s)) | set(LD_RE.findall(s)) | set(LOC_RE.findall(s))
            for url in urls:
                p = target_path(url.strip(), root)
                if p is None:
                    continue
                checked += 1
                if not os.path.exists(p):
                    broken.append((os.path.relpath(fp, HERE), url))
    print(f"files {files}, internal links {checked}, broken {len(broken)}")
    for f, u in sorted(broken):
        print(f"  {f}: {u[:120]!r}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
