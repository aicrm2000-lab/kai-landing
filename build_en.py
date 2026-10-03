# -*- coding: utf-8 -*-
"""Статическая английская версия лендинга: en/index.html из index.html.

Лендинг двуязычный через data-ru/data-en и JS-переключатель, но поисковые и ИИ-краулеры видят
только русский HTML (html lang="ru"). Эта сборка «прожигает» data-en в разметку, ставит lang="en",
английские title/description/OG, canonical /en/ и hreflang, переписывает относительные пути на ../
и делает английский языком по умолчанию для скриптов страницы. Запуск: py -3.12 build_en.py
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "index.html")
OUT_DIR = os.path.join(HERE, "en")
BASE = "https://aicrm2000-lab.github.io/kai-landing/"

EN_META = {
    "title": "Kai — Set up your CRM without developers | AI assistant for amoCRM and Kommo",
    "description": ("Kai sets up amoCRM and Kommo from a plain-language message in Telegram or your browser: "
                    "pipelines, fields, tasks, automations, analytics. 3 days free, no card."),
    "og_title": "Kai — AI assistant that sets up your CRM",
    "og_description": ("Set up amoCRM and Kommo by chatting: pipelines, fields, tasks, automations, integrations, "
                       "analytics. 65 actions. 3 days free, no card."),
    "keywords": ("amoCRM, Kommo, Bitrix24, CRM setup, AI assistant, CRM automation, Telegram CRM bot, sales pipelines, "
                 "amoCRM API, Kommo API, CRM without developers"),
}
EN_LD = {
    "description": ("AI assistant that sets up and manages amoCRM and Kommo from your browser or Telegram. "
                    "65 actions: pipelines, fields, stages, deals, contacts, automations."),
    "featureList": ["AI consulting on your CRM structure", "Sales pipelines and stages", "Custom fields for deals, contacts and companies",
                    "Automations: Digital Pipeline, triggers, Salesbot", "Technical specification as a PDF",
                    "Voice message recognition", "One-click OAuth connection"],
    "faq": [
        ("What can Kai do?", "Kai is an AI assistant that sets up amoCRM and Kommo from your browser or Telegram: it creates pipelines, "
                             "fields, stages, deals, contacts, tasks and automations. 65 actions without developers."),
        ("Is it safe? Will you get access to my data?", "Kai works through the official amoCRM/Kommo OAuth 2.0. We never see your password. "
                                                        "You can revoke access at any time in your CRM settings."),
        ("How much does Kai cost?", "Three plans: Start — €29/month (1 CRM), Pro — €59/month (3 CRMs), Max — €119/month (10 CRMs). "
                                    "The first 3 days are free."),
        ("Does Kai work with Kommo?", "Yes, Kai supports both amoCRM and Kommo. The API is compatible, the connection goes through OAuth."),
        ("Does Kai work with Bitrix24?", "Yes, in beta: Bitrix24 connects through an inbound webhook, Kai sets up pipelines, "
                                         "stages, fields, deals, contacts and tasks and runs the analytics. Automations inside "
                                         "Bitrix24 and widgets are not available yet. amoCRM and Kommo are fully supported."),
        ("Can I try it for free?", "Yes, the first 3 days are free with no limits. Try it risk-free."),
    ],
}


def _burn_attr_variants(m: "re.Match") -> str:
    """title / aria-label с data-en-title / data-en-label → английское значение прямо в атрибуте."""
    tag = m.group(0)
    for attr, variant in (("title", "data-en-title"), ("aria-label", "data-en-label")):
        v = re.search(rf'\s{variant}="([^"]*)"', tag)
        if v:
            if re.search(rf'\s{attr}="', tag):
                tag = re.sub(rf'\s{attr}="[^"]*"', f' {attr}="{v.group(1)}"', tag, count=1)
            else:
                tag = tag[:-1] + f' {attr}="{v.group(1)}">'
    return tag


def _english_jsonld(html: str) -> str:
    """Два блока ld+json: описание, featureList и вопросы FAQ — по-английски, inLanguage = en."""
    import json
    blocks = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S))
    for m in reversed(blocks):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        d["inLanguage"] = "en"
        if d.get("@type") == "SoftwareApplication":
            d["description"] = EN_LD["description"]
            d["featureList"] = EN_LD["featureList"]
        elif d.get("@type") == "FAQPage":
            for q, (name, text) in zip(d.get("mainEntity", []), EN_LD["faq"]):
                q["name"] = name
                q["acceptedAnswer"]["text"] = text
        new = '<script type="application/ld+json">\n' + json.dumps(d, ensure_ascii=False, indent=2) + '\n</script>'
        html = html[:m.start()] + new + html[m.end():]
    return html


def apply_data_en(html: str) -> str:
    """Для каждого элемента с data-en заменяем содержимое на data-en (там может быть разметка)."""
    # значения атрибутов могут содержать разметку (<br>, <em>, <span>), поэтому «>» внутри кавычек не конец тега
    tag_re = re.compile(r'<(?P<tag>[a-zA-Z][\w-]*)(?P<attrs>(?:[^>"]|"[^"]*")*?)\sdata-en="(?P<en>[^"]*)"(?P<rest>(?:[^>"]|"[^"]*")*)>', re.S)
    out, pos = [], 0
    for m in tag_re.finditer(html):
        tag = m.group("tag")
        en = m.group("en").replace("&quot;", '"')
        start_tag = m.group(0)
        if tag in ("input", "img", "meta", "link", "br"):
            continue
        close = f"</{tag}>"
        # ищем закрывающий тег с учётом вложенности того же тега
        depth, i = 1, m.end()
        open_re = re.compile(rf'<{tag}\b(?:[^>"]|"[^"]*")*>|</{tag}>', re.S)
        end = None
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
        if end is None:
            continue
        out.append(html[pos:m.start()])
        out.append(start_tag)
        out.append(en)
        pos = end
    out.append(html[pos:])
    return "".join(out)


def check_action_count(src: str) -> int:
    """Одно число действий на всей странице: значков в сетке API = счётчик под сеткой = все «NN действий» /
    «NN actions» (в RU-исходнике и в английских мета/JSON-LD этого файла). Разъехалось — сборка падает,
    чтобы новое действие не оставило «60+», «65» и «68» на одной странице."""
    n = len(re.findall(r'<div class="api-badge"', src))
    texts = src + json.dumps(EN_META, ensure_ascii=False) + json.dumps(EN_LD, ensure_ascii=False)
    said = re.findall(r"(\d+)\+?\s*(?:API-)?(?:действий|actions)\b", texts)
    said += re.findall(r'data-count="(\d+)">\d+</strong>\s*<span data-ru="действий', src)
    bad = sorted({x for x in said if int(x) != n})
    if not n or not said or bad:
        raise SystemExit(f"Число действий разъехалось: значков {n}, в текстах {sorted(set(said))} — поправь тексты или значки")
    return n


def main() -> None:
    html = io.open(SRC, encoding="utf-8").read()
    n_actions = check_action_count(html)
    html = apply_data_en(html)
    html = html.replace('<html lang="ru"', '<html lang="en"', 1)
    html = re.sub(r"<title>.*?</title>", f"<title>{EN_META['title']}</title>", html, count=1, flags=re.S)
    html = re.sub(r'(<meta name="description" content=")[^"]*(")', rf"\g<1>{EN_META['description']}\2", html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{EN_META['og_title']}\2", html, count=1)
    html = re.sub(r'(<meta property="og:description" content=")[^"]*(")', rf"\g<1>{EN_META['og_description']}\2", html, count=1)
    html = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', rf"\g<1>{EN_META['og_title']}\2", html, count=1)
    html = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', rf"\g<1>{EN_META['og_description']}\2", html, count=1)
    html = html.replace('<meta property="og:locale" content="ru_RU">', '<meta property="og:locale" content="en_US">')
    html = html.replace('<meta property="og:locale:alternate" content="en_US">', '<meta property="og:locale:alternate" content="ru_RU">')
    html = html.replace(f'<link rel="canonical" href="{BASE}">', f'<link rel="canonical" href="{BASE}en/">')
    html = html.replace(f'<meta property="og:url" content="{BASE}">', f'<meta property="og:url" content="{BASE}en/">')
    # относительные пути (картинки, страницы политики) → на уровень выше; якоря и абсолютные не трогаем
    html = re.sub(r'\b(src|href)="(?!https?:|//|#|mailto:|tel:|data:|\.\./|/|javascript:)([\w][^"]*)"',
                  lambda m: f'{m.group(1)}="../{m.group(2)}"', html)
    html = re.sub(r"url\((['\"]?)(?!https?:|//|data:|\.\./|/|#)([\w][^'\")]*)", lambda m: f"url({m.group(1)}../{m.group(2)}", html)
    for prop in ("og:image", "twitter:image"):
        html = re.sub(rf'(<meta (?:property|name)="{prop}" content=")(?!https?:)([^"]+)"',
                      lambda m: f'{m.group(1)}{BASE}{m.group(2)}"', html)
    # английские версии политик
    for p in ("privacy", "terms", "refund"):
        html = html.replace(f'href="../{p}.html"', f'href="../{p}-en.html"')
        # applyLang() перезаписывает эти ссылки из скрипта, а cookie-текст держит ссылку внутри значения атрибута
        html = html.replace(f"'{p}-en.html' : '{p}.html'", f"'../{p}-en.html' : '../{p}.html'")
        html = html.replace(f"href='{p}-en.html'", f"href='../{p}-en.html'").replace(f"href='{p}.html'", f"href='../{p}-en.html'")
    html = html.replace('href="../guides/"', 'href="../guides/en/"')
    # атрибуты title/aria-label с английскими вариантами
    html = re.sub(r'<(?P<tag>[a-zA-Z][\w-]*)(?P<attrs>(?:[^>"]|"[^"]*")*)>', _burn_attr_variants, html)
    # структурированные данные и ключевые слова — английские
    html = _english_jsonld(html)
    html = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{EN_META["keywords"]}">', html, count=1)
    # английский по умолчанию: не читаем сохранённый язык, уважаем только ?lang=
    html = html.replace("let currentLang = 'en';\ntry { currentLang = localStorage.getItem('kai_lang') || detectLang(); } catch (e) { currentLang = detectLang(); }",
                        "let currentLang = 'en';   // статическая EN-версия: язык страницы — английский")
    # JSON-LD inLanguage
    html = html.replace('"inLanguage": "ru"', '"inLanguage": "en"').replace('"inLanguage":"ru"', '"inLanguage":"en"')
    os.makedirs(OUT_DIR, exist_ok=True)
    io.open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8", newline="\n").write(html)
    n_ru = len(re.findall(r'data-ru="', html))
    # контроль: в теле не должно остаться русского текста вне скриптов, стилей и атрибутов
    body = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", html[html.find("<body"):])
    text = re.sub(r'<(?:[^>"]|"[^"]*")*>', "\x00", body)   # теги убираем с учётом «>» внутри значений атрибутов
    left = [t.strip() for t in text.split("\x00") if re.search(r"[А-Яа-яЁё]", t)]
    print(f"en/index.html: {len(html) // 1024} KB, data-ru attrs kept: {n_ru}, Russian text nodes left: {len(left)}, "
          f"actions: {n_actions} everywhere")
    for t in left[:8]:
        print("   RU:", t[:70])


if __name__ == "__main__":
    main()
