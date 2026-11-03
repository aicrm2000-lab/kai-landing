# -*- coding: utf-8 -*-
"""Сборка раздела гайдов: guides/<slug>.html (RU), guides/en/<slug>.html (EN), guides/<lang>/ на остальных языках (через
i18n_pages.py и словари i18n/pages/<lang>.json), индексы и sitemap.xml (в нём же кейсы и политики всех языков).

Вход: guides.json — [{"slug", "title_ru", "title_en", "desc_ru", "desc_en", "html_ru", "html_en"}].
Запуск: py -3.12 build_guides.py   (после build_en.py — sitemap собирается по факту файлов)
"""
import datetime as dt
import html
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://aii-crm.com/"
TODAY = dt.date.today().isoformat()
MARK = ('<svg viewBox="0 0 48 48" width="28" height="28" aria-hidden="true"><path d="M39.21 19.58A15.84 15.84 0 1 1 23.5 8.17" fill="none" '
        'stroke="var(--accent)" stroke-width="6.72" stroke-linecap="round"/><circle cx="33.12" cy="11.44" r="3.36" fill="var(--accent-2)"/></svg>')

KEYWORDS_RU = "настройка amoCRM, настройка Kommo, воронка продаж amoCRM, автоматизация amoCRM, автоматизация Kommo, CRM без интегратора, ИИ-ассистент для CRM, AI для amoCRM, гайды amoCRM, гайды Kommo, Kai CRM, подключить ИИ-агента к самописной CRM, ИИ для кастомной CRM, своя CRM по API"
KEYWORDS_EN = "amoCRM setup, Kommo setup, Kommo automation, amoCRM pipeline, CRM without integrator, AI assistant for CRM, AI for Kommo, Kommo guides, amoCRM guides, Kai CRM, connect AI agent to custom CRM, in-house CRM AI assistant, custom CRM via API"

INDEX_CSS = """
:root{--bg:#0B0A14;--bg-1:#100E20;--bg-2:#171332;--border:#241D45;--ink:#F4F2FF;--text:#CBC5E4;--muted:#8B83AC;--accent:#7C5CFF;--accent-2:#A78BFA}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:17px/1.6 'Manrope',system-ui,sans-serif;padding:0 16px 64px}
.wrap{max-width:760px;margin:0 auto}header{display:flex;align-items:center;gap:12px;padding:22px 0;border-bottom:1px solid var(--border)}
header a{color:var(--ink);text-decoration:none;font-weight:700}header .brand{display:flex;align-items:center;gap:10px;color:var(--ink);text-decoration:none;font-weight:700}header .brand svg{flex:0 0 28px}header nav{margin-left:auto;display:flex;gap:18px;font-size:14px}header nav a{color:var(--muted);font-weight:500}
h1{font-size:clamp(28px,5vw,40px);line-height:1.15;letter-spacing:-.02em;color:var(--ink);margin:40px 0 12px}
.lead{color:var(--text);max-width:62ch}.card{display:block;border:1px solid var(--border);background:var(--bg-1);border-radius:16px;padding:20px 22px;margin-top:14px;text-decoration:none;color:inherit;transition:border-color .15s}
.card:hover{border-color:var(--accent)}.card b{display:block;color:var(--ink);font-size:19px;margin-bottom:6px}.card span{color:var(--muted);font-size:15px}
.cta{margin-top:36px;padding:22px;border-radius:16px;background:var(--bg-2);border:1px solid var(--border)}.cta a{display:inline-block;margin:10px 10px 0 0;padding:12px 18px;border-radius:999px;background:linear-gradient(135deg,#7C5CFF,#A78BFA);color:#fff;text-decoration:none;font-weight:700}
.cta a.alt{background:none;border:1px solid var(--border);color:var(--accent-2)}footer{margin-top:40px;color:var(--muted);font-size:13px}
"""


IX = {   # строки индекса гайдов; другие языки — перевод английских через словарь i18n/pages/<lang>.json
    "ru": {"title": "Гайды: настройка amoCRM, Kommo, Bitrix24 и своей CRM без программиста",
           "desc": "Пошаговые гайды по воронкам, полям, автоматизациям и ИИ-инструментам для amoCRM, Kommo, Bitrix24 и своей (самописной) CRM — руками, через интегратора и через Kai.",
           "keywords": KEYWORDS_RU, "home": "на главную", "plans": "Тарифы", "cases_title": "Примеры: было → стало",
           "cases_desc": "Четыре ситуации в amoCRM и Kommo: воронка до, сообщение Kai, что он сделал, воронка после.",
           "cta": "Хотите, чтобы это сделал Kai?", "cta_tg": "Попробовать в Telegram", "cta_chat": "Открыть веб-чат", "privacy": "Конфиденциальность"},
    "en": {"title": "Guides: amoCRM, Kommo, Bitrix24 and custom CRM setup without developers",
           "desc": "Step-by-step guides on pipelines, fields, automations and AI tools for amoCRM, Kommo, Bitrix24 and your own (custom) CRM — by hand, via an integrator, or with Kai.",
           "keywords": KEYWORDS_EN, "home": "home", "plans": "Plans", "cases_title": "Examples: before → after",
           "cases_desc": "Four situations in amoCRM and Kommo: the pipeline before, the message to Kai, what it did, the pipeline after.",
           "cta": "Want Kai to do it for you?", "cta_tg": "Try in Telegram", "cta_chat": "Open web chat", "privacy": "Privacy"},
}

_m = re.search(r'<link rel="icon" href="([^"]+)"', io.open(os.path.join(HERE, "index.html"), encoding="utf-8").read())
FAVICON = _m.group(1) if _m else ""


def index_page(lang: str, guides: list, d=None) -> str:
    """индекс гайдов: ru/en — строки из IX, другие языки — через словарь d (i18n_pages.Dict), английский — запасной"""
    import i18n_pages
    ru, en = lang == "ru", lang == "en"
    L = IX[lang] if lang in IX else {k: d.t(v) for k, v in IX["en"].items()}
    title_of = (lambda g: g["title_ru"]) if ru else (lambda g: g["title_en"]) if en else (lambda g: d.t(g["title_en"]))
    desc_of = (lambda g: g["desc_ru"]) if ru else (lambda g: g["desc_en"]) if en else (lambda g: d.t(g["desc_en"]))
    items = "".join(f'<a class="card" href="{g["slug"]}.html"><b>{html.escape(title_of(g))}</b><span>{html.escape(desc_of(g))}</span></a>' for g in guides)
    t, dsc = L["title"], L["desc"]
    self_url = BASE + i18n_pages.guides_index_path(lang)
    up = "../" if ru else "../../"
    home = up if ru else f"{up}{lang}/"
    chat = "https://app.aii-crm.com/chat?lang=" + ("ru" if ru else "en")
    switch = f'<a href="{BASE}guides/en/">EN</a>' if ru else f'<a href="{BASE}guides/">RU</a>' if en else f'<a href="{BASE}guides/en/" hreflang="en">EN</a>'
    cases = up + i18n_pages.cases_path(lang)
    privacy = up + i18n_pages.policy_path("privacy")(lang)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(){{try{{var h=document.documentElement,q=new URLSearchParams(location.search),d=new Date(),m=d.getMonth(),n=d.getDate(),dm=/(^|[.])aii-crm[.]com$/.test(location.hostname)?';domain=aii-crm.com':'',act=null,apr=-1;[['hw',(m===9&&n>=25)||(m===10&&n<=2)],['ny',(m===11&&n>=20)||(m===0&&n<=10)]].forEach(function(s){{var k=s[0],season=s[1],on=season,st=null,p=q.get(k),pr=season?1:0;try{{st=localStorage.getItem('kai_'+k);}}catch(e){{}}try{{var ck=document.cookie.match(new RegExp('(?:^|; )kai_'+k+'=([01])'));if(ck)st=ck[1];if(st==='0'||st==='1'){{document.cookie='kai_'+k+'='+st+';max-age=31536000;path=/;SameSite=Lax'+dm;if(ck)localStorage.setItem('kai_'+k,st);}}}}catch(e){{}}if(st==='0')on=false;else if(st==='1')on=true;if(p==='1'){{on=true;pr=2;}}else if(p==='0')on=false;if(on&&(!act||pr>apr)){{act=k;apr=pr;}}}});if(act)h.classList.add(act);}}catch(e){{}}}})();</script>
<title>{html.escape(t)} | Kai</title>
<meta name="description" content="{html.escape(dsc)}">
<meta name="keywords" content="{html.escape(L["keywords"])}">
<link rel="canonical" href="{self_url}">
{i18n_pages.hreflang_block(i18n_pages.guides_index_path)}
<meta property="og:type" content="website"><meta property="og:site_name" content="Kai"><meta property="og:locale" content="{i18n_pages.LOCALES[lang]}">
<meta property="og:title" content="{html.escape(t)}"><meta property="og:description" content="{html.escape(dsc)}"><meta property="og:image" content="{BASE}og-image.png"><meta property="og:url" content="{self_url}">
<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap">
<style>{INDEX_CSS}/* Halloween (html.hw): та же палитра, что на главной, чате и в кабинете */
html.hw{{--bg:#0C0A0E;--bg-1:#140F13;--bg-2:#1C1518;--border:#2E201C;--ink:#FBF5EE;--text:#D9CFC8;--muted:#9A8A86;--dim:#6E5B58;--accent:#FF7A1A;--accent-2:#FFB347}}
/* New Year (html.ny): та же палитра, что на главной, чате и в кабинете */
html.ny{{--bg:#070B19;--bg-1:#0C1226;--bg-2:#121A33;--border:#223055;--ink:#F4F7FF;--text:#C9D3EC;--muted:#8D98BD;--dim:#5F6B92;--accent:#21A66D;--accent-2:#F5C451}}
html.ny .badge.crm{{border-color:rgba(33,166,109,.45)}}html.ny .msg.me{{background:rgba(33,166,109,.18);border-color:rgba(33,166,109,.45)}}
html.hw .badge.crm{{border-color:rgba(255,122,26,.45)}}html.hw .msg.me{{background:rgba(255,122,26,.18);border-color:rgba(255,122,26,.45)}}
</style>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": t, "description": dsc, "url": self_url, "inLanguage": lang,
    "isPartOf": {"@type": "WebSite", "name": "Kai", "url": BASE},
    "hasPart": [{"@type": "Article", "headline": title_of(g), "url": self_url + g["slug"] + ".html"} for g in guides]}, ensure_ascii=False)}</script>
</head>
<body><div class="wrap">
<header><a class="brand" href="{home}" aria-label="Kai — {html.escape(L["home"])}">{MARK}<span>Kai</span></a><nav><a href="{home}#pricing">{html.escape(L["plans"])}</a>{switch}</nav></header>
<h1>{html.escape(t)}</h1>
<p class="lead">{html.escape(dsc)}</p>
<a class="card" href="{cases}" style="border-color:var(--accent)"><b>{html.escape(L["cases_title"])}</b><span>{html.escape(L["cases_desc"])}</span></a>
{items}
<div class="cta"><b style="color:var(--ink)">{html.escape(L["cta"])}</b><br>
<a href="https://t.me/aiicrm_bot">{html.escape(L["cta_tg"])}</a><a class="alt" href="{chat}">{html.escape(L["cta_chat"])}</a></div>
<footer>© 2026 Kai · <a href="{privacy}" style="color:var(--muted)">{html.escape(L["privacy"])}</a></footer>
</div></body></html>
"""


def main() -> None:
    guides = json.load(io.open(os.path.join(HERE, "guides.json"), encoding="utf-8"))
    os.makedirs(os.path.join(HERE, "guides", "en"), exist_ok=True)
    import i18n_pages
    for g in guides:   # hreflang на все 12 языков и в русской, и в английской версии
        hl = i18n_pages.guide_path(g["slug"])
        io.open(os.path.join(HERE, "guides", f"{g['slug']}.html"), "w", encoding="utf-8", newline="\n").write(i18n_pages.set_hreflang(g["html_ru"], hl))
        io.open(os.path.join(HERE, "guides", "en", f"{g['slug']}.html"), "w", encoding="utf-8", newline="\n").write(i18n_pages.set_hreflang(g["html_en"], hl))
    io.open(os.path.join(HERE, "guides", "index.html"), "w", encoding="utf-8", newline="\n").write(index_page("ru", guides))
    io.open(os.path.join(HERE, "guides", "en", "index.html"), "w", encoding="utf-8", newline="\n").write(index_page("en", guides))
    langs = i18n_pages.build_all()   # guides/<lang>/, cases/<lang>/, политики -<lang> для языков со словарём i18n/pages/<lang>.json
    # sitemap: главная, /en/, политики, гайды
    urls = [("", "1.0", "weekly"), ("en/", "0.9", "weekly"), ("de/", "0.9", "weekly"), ("fr/", "0.9", "weekly"), ("es/", "0.9", "weekly"), ("pl/", "0.9", "weekly"), ("pt/", "0.9", "weekly"), ("it/", "0.9", "weekly"), ("tr/", "0.9", "weekly"), ("be/", "0.9", "weekly"), ("uk/", "0.9", "weekly"), ("ro/", "0.9", "weekly"), ("guides/", "0.8", "weekly"), ("guides/en/", "0.8", "weekly"), ("cases/", "0.9", "monthly"), ("cases/en/", "0.9", "monthly")]
    urls += [(f"guides/{g['slug']}.html", "0.8", "monthly") for g in guides] + [(f"guides/en/{g['slug']}.html", "0.8", "monthly") for g in guides]
    urls += [(p, "0.3", "monthly") for p in ("privacy.html", "privacy-en.html", "terms.html", "terms-en.html", "refund.html", "refund-en.html")]
    for c in langs:
        urls += [(f"guides/{c}/", "0.8", "weekly"), (f"cases/{c}/", "0.9", "monthly")]
        urls += [(f"guides/{c}/{g['slug']}.html", "0.8", "monthly") for g in guides]
        urls += [(f"{p}-{c}.html", "0.3", "monthly") for p in ("privacy", "terms", "refund")]
    body = "".join(f"  <url>\n    <loc>{BASE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{c}</changefreq>\n    <priority>{p}</priority>\n  </url>\n" for u, p, c in urls)
    io.open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")
    print(f"guides: {len(guides)} × {2 + len(langs)} языков, sitemap: {len(urls)} URL")

    import seo_meta   # короткие title/description для выдачи (i18n/seo/<lang>.json)
    seo_meta.apply()


if __name__ == "__main__":
    main()
