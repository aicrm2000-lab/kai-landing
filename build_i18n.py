# -*- coding: utf-8 -*-
"""Статические версии лендинга на других языках: <lang>/index.html из index.html + i18n/<lang>.json.

Русский исходник index.html двуязычный через data-ru/data-en (JS-переключатель), английскую версию en/ собирает
build_en.py. Для остальных языков словарь i18n/<lang>.json (ключ — английская строка из data-en, значение — перевод;
плюс meta, ld, ui) «прожигается» в разметку: тексты элементов, title/aria-label, праздничные варианты data-hw-en/
data-ny-en и имена действий data-act-en. Атрибуты data-ru/data-en убираются (переключения на странице нет, страница
легче), html lang=<lang>, data-page-lang, title/description/keywords/OG, canonical /<lang>/, hreflang остаётся общим
из исходника, JSON-LD (описание, featureList, FAQ) и inLanguage на языке, ссылки в app с ?lang=en (Kai говорит RU/EN),
политики и гайды — английские, под подзаголовком hero — фраза про языки Kai. Строки без перевода остаются английскими
и считаются; перевод с другим набором HTML-тегов или цифр отбрасывается (fallback EN) и тоже считается.
Запуск: py -3.12 build_i18n.py [de fr …] (без аргументов — все словари в i18n/, кроме source.json)."""
import io
import json
import os
import re
import sys

from build_en import apply_data_en as _apply_data_en_unused  # noqa: F401  (тот же контракт разметки, см. apply_data)
from build_en import check_action_count

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "index.html")
BASE = "https://aii-crm.com/"
TAG_RE = re.compile(r'<(?P<tag>[a-zA-Z][\w-]*)(?P<attrs>(?:[^>"]|"[^"]*")*?)\sdata-en="(?P<en>[^"]*)"(?P<rest>(?:[^>"]|"[^"]*")*)>', re.S)
ANY_TAG = re.compile(r'<(?P<tag>[a-zA-Z][\w-]*)(?P<attrs>(?:[^>"]|"[^"]*")*)>', re.S)
VOID = ("input", "img", "meta", "link", "br")


def attr(v: str) -> str:
    return v.replace('"', "&quot;")


class Dict:
    def __init__(self, data: dict):
        self.data = data
        self.strings = data["strings"]
        self.missing, self.rejected = [], []

    def t(self, en: str) -> str:
        """перевод английской строки (ключ — как в атрибуте, с &quot;), с проверкой тегов и цифр"""
        v = self.strings.get(en)
        if v is None:
            self.missing.append(en)
            return en
        if re.findall(r"<[^>]+>", v) != re.findall(r"<[^>]+>", en) or sorted(re.findall(r"\d+", v)) != sorted(re.findall(r"\d+", en)):
            self.rejected.append(en)
            return en
        return v


def apply_data(html: str, d: Dict) -> str:
    """содержимое каждого элемента с data-en → перевод (en как fallback); разметка внутри значения допустима"""
    out, pos = [], 0
    for m in TAG_RE.finditer(html):
        tag = m.group("tag")
        if tag in VOID:
            continue
        depth, i, end = 1, m.end(), None
        open_re = re.compile(rf'<{tag}\b(?:[^>"]|"[^"]*")*>|</{tag}>', re.S)
        while depth:
            n = open_re.search(html, i)
            if not n:
                break
            if n.group(0).startswith("</"):
                depth -= 1
                if depth == 0:
                    end = n.start()
                    break
            else:
                depth += 1
            i = n.end()
        if end is None or m.start() < pos:
            continue
        out.append(html[pos:m.start()])
        out.append(m.group(0))
        out.append(d.t(m.group("en")).replace("&quot;", '"'))
        pos = end
    out.append(html[pos:])
    return "".join(out)


def burn_attrs(html: str, d: Dict) -> str:
    """title / aria-label из data-en-title / data-en-label → перевод в самом атрибуте; data-act-en, data-hw-en, data-ny-en → перевод"""
    def one(m):
        tag = m.group(0)
        for a, variant in (("title", "data-en-title"), ("aria-label", "data-en-label")):
            v = re.search(rf'\s{variant}="([^"]*)"', tag)
            if v:
                val = attr(d.t(v.group(1)))
                if re.search(rf'\s{a}="', tag):
                    tag = re.sub(rf'\s{a}="[^"]*"', f' {a}="{val}"', tag, count=1)
                else:
                    tag = tag[:-1] + f' {a}="{val}">'
        tag = re.sub(r'\s(data-act-en|data-hw-en|data-ny-en)="([^"]*)"', lambda v: f' {v.group(1)}="{attr(d.t(v.group(2)))}"', tag)
        return tag
    return ANY_TAG.sub(one, html)


def strip_switch_attrs(html: str) -> str:
    """без переключателя RU/EN на странице эти атрибуты не нужны (минус ~60 КБ); праздничные варианты остаются"""
    return re.sub(r'\s(?:data-ru|data-en|data-ru-title|data-en-title|data-ru-label|data-en-label|data-ru-href|data-en-href|data-hw-ru|data-ny-ru|data-act-ru)="[^"]*"', "", html)


def localized_jsonld(html: str, d: Dict, code: str) -> str:
    ld = d.data["ld"]
    blocks = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S))
    for m in reversed(blocks):
        try:
            obj = json.loads(m.group(1))
        except ValueError:
            continue
        obj["inLanguage"] = code
        if obj.get("@type") == "SoftwareApplication":
            obj["description"] = ld["description"]
            obj["featureList"] = ld["featureList"]
        elif obj.get("@type") == "FAQPage":
            for q, (name, text) in zip(obj.get("mainEntity", []), ld["faq"]):
                q["name"] = name
                q["acceptedAnswer"]["text"] = text
        new = '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>"
        html = html[:m.start()] + new + html[m.end():]
    return html


def build(code: str) -> str:
    d = Dict(json.load(io.open(os.path.join(HERE, "i18n", f"{code}.json"), encoding="utf-8")))
    meta, ui, locale = d.data["meta"], d.data["ui"], d.data.get("locale", f"{code}_{code.upper()}")
    html = io.open(SRC, encoding="utf-8").read()
    n_actions = check_action_count(html)
    html = apply_data(html, d)
    html = burn_attrs(html, d)
    html = strip_switch_attrs(html)
    html = html.replace('<html lang="ru"', f'<html lang="{code}" data-page-lang="{code}"', 1)
    html = re.sub(r"<title>.*?</title>", f"<title>{meta['title']}</title>", html, count=1, flags=re.S)
    for tag_re, val in ((r'(<meta name="description" content=")[^"]*(")', meta["description"]),
                        (r'(<meta property="og:title" content=")[^"]*(")', meta["og_title"]),
                        (r'(<meta property="og:description" content=")[^"]*(")', meta["og_description"]),
                        (r'(<meta name="twitter:title" content=")[^"]*(")', meta["og_title"]),
                        (r'(<meta name="twitter:description" content=")[^"]*(")', meta["og_description"]),
                        (r'(<meta name="keywords" content=")[^"]*(")', meta["keywords"])):
        html = re.sub(tag_re, lambda m, v=val: m.group(1) + attr(v) + m.group(2), html, count=1)
    html = html.replace('<meta property="og:locale" content="ru_RU">', f'<meta property="og:locale" content="{locale}">')
    html = html.replace('<meta property="og:locale:alternate" content="en_US">',
                        '<meta property="og:locale:alternate" content="en_US">\n<meta property="og:locale:alternate" content="ru_RU">')
    html = html.replace(f'<link rel="canonical" href="{BASE}">', f'<link rel="canonical" href="{BASE}{code}/">')
    html = html.replace(f'<meta property="og:url" content="{BASE}">', f'<meta property="og:url" content="{BASE}{code}/">')
    # относительные пути → на уровень выше; якоря и абсолютные не трогаем (как в build_en)
    html = re.sub(r'\b(src|href)="(?!https?:|//|#|mailto:|tel:|data:|\.\./|/|javascript:)([\w][^"]*)"',
                  lambda m: f'{m.group(1)}="../{m.group(2)}"', html)
    html = re.sub(r"url\((['\"]?)(?!https?:|//|data:|\.\./|/|#)([\w][^'\")]*)", lambda m: f"url({m.group(1)}../{m.group(2)}", html)
    for prop in ("og:image", "twitter:image"):
        html = re.sub(rf'(<meta (?:property|name)="{prop}" content=")(?!https?:)([^"]+)"',
                      lambda m: f'{m.group(1)}{BASE}{m.group(2)}"', html)
    for p in ("privacy", "terms", "refund"):   # политики и гайды — английские
        html = html.replace(f'href="../{p}.html"', f'href="../{p}-en.html"')
        html = html.replace(f"'{p}-en.html' : '{p}.html'", f"'../{p}-en.html' : '../{p}.html'")
        html = html.replace(f"href='{p}-en.html'", f"href='../{p}-en.html'").replace(f"href='{p}.html'", f"href='../{p}-en.html'")
    html = html.replace('href="../guides/"', 'href="../guides/en/"')
    for _p in ("account", "login", "signup", "chat", "docs/custom-crm"):   # Kai говорит по-английски и по-русски
        html = html.replace(f'app.aii-crm.com/{_p}?lang=ru"', f'app.aii-crm.com/{_p}?lang=en"')
    html = localized_jsonld(html, d, code)
    html = html.replace("let currentLang = 'en';\ntry { currentLang = localStorage.getItem('kai_lang') || detectLang(); } catch (e) { currentLang = detectLang(); }",
                        "let currentLang = 'en';   // статическая версия на языке страницы: тексты не переключаются, app — по-английски")
    html = html.replace("  document.documentElement.lang = lang;\n", "  /* html lang — язык страницы, скрипты считают её английской */\n")
    html = html.replace('"inLanguage": "ru"', f'"inLanguage": "{code}"').replace('"inLanguage":"ru"', f'"inLanguage":"{code}"')
    # словарь для скриптов (слова частиц, подписи праздничных кнопок) и фраза про языки Kai под подзаголовком
    l10n = {"lang": code, "words": ui.get("words"), "words_ny": ui.get("words_ny"),
            "ui": {k: ui.get(k) for k in ("theme_hw", "theme_ny", "turn_on", "turn_off", "lang_label")}}
    html = html.replace("<head>\n", "<head>\n<script>window.KAI_L10N=" + json.dumps(l10n, ensure_ascii=False) + ";</script>\n", 1)
    note = ui.get("kai_note")
    if note:
        html = re.sub(r'(<p class="hero-note"[^>]*>)(.*?)(</p>)', lambda m: m.group(1) + m.group(2) + f'<span class="hero-note-lang">{note}</span>' + m.group(3), html, count=1, flags=re.S)
    out_dir = os.path.join(HERE, code)
    os.makedirs(out_dir, exist_ok=True)
    io.open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n").write(html)
    body = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", html[html.find("<body"):])
    body = re.sub(r'<ul class="lang-list"[\s\S]*?</ul>', " ", body)   # «Русский» в меню языков — не забытый русский
    text = re.sub(r'<(?:[^>"]|"[^"]*")*>', "\x00", body)
    left_ru = [] if code in ("uk", "be") else [t.strip() for t in text.split("\x00") if re.search(r"[А-Яа-яЁё]", t)]   # кириллица у uk/be своя
    print(f"{code}/index.html: {len(html) // 1024} KB, missing: {len(set(d.missing))}, rejected: {len(set(d.rejected))}, "
          f"Russian text nodes left: {len(left_ru)}, actions: {n_actions}")
    for t in sorted(set(d.rejected))[:6]:
        print("   rejected:", t[:80])
    for t in left_ru[:4]:
        print("   RU:", t[:70])
    return html


def main() -> None:
    codes = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(os.path.join(HERE, "i18n")) if f.endswith(".json") and f != "source.json")
    for code in codes:
        build(code)


if __name__ == "__main__":
    main()
