# -*- coding: utf-8 -*-
"""Короткие <title> и meta description для выдачи (Bing: title ≤ 70, description 25–160; Google режет примерно там же).

Длинные исходные тексты остаются в гайдах, словарях и JSON-LD (это ключи переводов — их не трогаем), а для выдачи
поверх собранных страниц накладываются короткие версии из i18n/seo/<lang>.json:
    {"<путь от корня>": {"title": "...", "description": "..."}}   (путь: "" — главная, "de/", "guides/de/x.html", …)
og:title/og:description не трогаются (соцсети показывают длинные), меняются только <title> и meta description.

Команды:  py -3.12 seo_meta.py audit [lang …]   → нарушения по собранным страницам (с учётом наложения)
          py -3.12 seo_meta.py todo [lang …]     → i18n/seo/todo-<lang>.json: что укоротить (текущие тексты)
          py -3.12 seo_meta.py apply             → наложить (его же вызывают build_en, build_i18n, build_cases, build_guides)"""
import html
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://aii-crm.com/"
SEO_DIR = os.path.join(HERE, "i18n", "seo")
TITLE_MAX, DESC_MIN, DESC_MAX = 70, 25, 160
LANGS = ["ru", "en", "de", "fr", "es", "pl", "pt", "it", "tr", "be", "uk", "ro"]


def urls() -> list:
    return re.findall(r"<loc>([^<]+)</loc>", io.open(os.path.join(HERE, "sitemap.xml"), encoding="utf-8").read())


def rel(u: str) -> str:
    return u[len(BASE):]


def local(path: str) -> str:
    p = os.path.join(HERE, *path.split("/")) if path else HERE
    return os.path.join(p, "index.html") if (path.endswith("/") or not path) else p


def lang_of(path: str) -> str:
    m = re.match(r"(?:guides/|cases/)?([a-z]{2})/", path)
    if m and m.group(1) in LANGS:
        return m.group(1)
    m = re.search(r"-([a-z]{2})\.html$", path)
    if m and m.group(1) in LANGS:
        return m.group(1)
    return "ru"


def read_meta(h: str):
    head = h[:h.find("</head>")]
    t = re.search(r"<title>(.*?)</title>", head, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', head)
    return (html.unescape(t.group(1).strip()) if t else None, html.unescape(d.group(1)) if d else None)


def bad_title(t) -> bool:
    return t is None or len(t) > TITLE_MAX


def bad_desc(d) -> bool:
    return d is None or not (DESC_MIN <= len(d) <= DESC_MAX)


def load_overrides() -> dict:
    out = {}
    if os.path.isdir(SEO_DIR):
        for f in sorted(os.listdir(SEO_DIR)):
            if re.fullmatch(r"[a-z]{2}\.json", f):
                out.update(json.load(io.open(os.path.join(SEO_DIR, f), encoding="utf-8")))
    return out


def esc(v: str) -> str:
    return html.escape(v, quote=True)


def apply(quiet: bool = False) -> int:
    """наложить короткие title/description на все существующие страницы из файлов i18n/seo/*.json"""
    ov, n = load_overrides(), 0
    for path, m in ov.items():
        fp = local(path)
        if not os.path.exists(fp):
            continue
        h = io.open(fp, encoding="utf-8").read()
        h0 = h
        if m.get("title"):
            h = re.sub(r"<title>.*?</title>", lambda _: f"<title>{esc(m['title'])}</title>", h, count=1, flags=re.S)
        if m.get("description"):
            h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda x: x.group(1) + esc(m["description"]) + x.group(2), h, count=1)
        if h != h0:
            io.open(fp, "w", encoding="utf-8", newline="\n").write(h)
            n += 1
    if not quiet:
        print(f"seo_meta: short title/description applied to {n} pages")
    return n


def audit(verbose: bool = True, codes=None) -> list:
    bad = []
    for u in urls():
        path = rel(u)
        if codes and lang_of(path) not in codes:
            continue
        fp = local(path)
        if not os.path.exists(fp):
            continue
        t, d = read_meta(io.open(fp, encoding="utf-8").read())
        if bad_title(t) or bad_desc(d):
            bad.append((path, t, d))
    if verbose:
        print(f"{len(bad)} pages break the limits (title ≤ {TITLE_MAX}, description {DESC_MIN}–{DESC_MAX})")
        for p, t, d in bad[:30]:
            print(f"  /{p}: title {len(t or '')}{' !' if bad_title(t) else ''}, description {len(d or '')}{' !' if bad_desc(d) else ''}")
    return bad


def todo(codes=None) -> None:
    os.makedirs(SEO_DIR, exist_ok=True)
    per = {}
    for path, t, d in audit(verbose=False):
        lang = lang_of(path)
        if codes and lang not in codes:
            continue
        item = {}
        if bad_title(t):
            item["title"] = t
        if bad_desc(d):
            item["description"] = d
        per.setdefault(lang, {})[path] = item
    for lang, items in per.items():
        fn = os.path.join(SEO_DIR, f"todo-{lang}.json")
        io.open(fn, "w", encoding="utf-8", newline="\n").write(json.dumps(items, ensure_ascii=False, indent=1))
        print(f"{lang}: {len(items)} pages → {os.path.relpath(fn, HERE)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "apply":
        apply()
    elif cmd == "audit":   # audit [lang …]
        sys.exit(1 if audit(codes=sys.argv[2:] or None) else 0)
    elif cmd == "todo":
        todo(sys.argv[2:] or None)
    else:
        print(__doc__)
