# -*- coding: utf-8 -*-
"""Сборка раздела гайдов: guides/<slug>.html (RU), guides/en/<slug>.html (EN), индексы и sitemap.xml.

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

KEYWORDS_RU = "настройка amoCRM, настройка Kommo, воронка продаж amoCRM, автоматизация amoCRM, автоматизация Kommo, CRM без интегратора, ИИ-ассистент для CRM, AI для amoCRM, гайды amoCRM, гайды Kommo, Kai CRM"
KEYWORDS_EN = "amoCRM setup, Kommo setup, Kommo automation, amoCRM pipeline, CRM without integrator, AI assistant for CRM, AI for Kommo, Kommo guides, amoCRM guides, Kai CRM"

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


_m = re.search(r'<link rel="icon" href="([^"]+)"', io.open(os.path.join(HERE, "index.html"), encoding="utf-8").read())
FAVICON = _m.group(1) if _m else ""


def index_page(lang: str, guides: list[dict]) -> str:
    ru = lang == "ru"
    items = "".join(
        f'<a class="card" href="{g["slug"]}.html"><b>{html.escape(g["title_ru" if ru else "title_en"])}</b>'
        f'<span>{html.escape(g["desc_ru" if ru else "desc_en"])}</span></a>' for g in guides)
    t = ("Гайды: настройка amoCRM и Kommo без программиста" if ru else "Guides: amoCRM and Kommo setup without developers")
    d = ("Пошаговые гайды по воронкам, полям, автоматизациям и ИИ-инструментам для amoCRM и Kommo — руками, через интегратора и через Kai."
         if ru else "Step-by-step guides on pipelines, fields, automations and AI tools for amoCRM and Kommo — by hand, via an integrator, or with Kai.")
    self_url = BASE + ("guides/" if ru else "guides/en/")
    alt_ru, alt_en = BASE + "guides/", BASE + "guides/en/"
    up = "../" if ru else "../../"
    chat = "https://app.aii-crm.com/chat?lang=" + lang
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(){{try{{var p=new URLSearchParams(location.search).get('hw'),d=new Date(),m=d.getMonth(),n=d.getDate(),on=(m===9&&n>=25)||(m===10&&n<=2),st=null;try{{st=localStorage.getItem('kai_hw');}}catch(e){{}}try{{var ck=document.cookie.match(/(?:^|; )kai_hw=([01])/);if(ck)st=ck[1];if(st==='0'||st==='1'){{document.cookie='kai_hw='+st+';max-age=31536000;path=/;SameSite=Lax'+(/(^|[.])aii-crm[.]com$/.test(location.hostname)?';domain=aii-crm.com':'');if(ck)localStorage.setItem('kai_hw',st);}}}}catch(e){{}}if(st==='0')on=false;else if(st==='1')on=true;if(p==='1')on=true;else if(p==='0')on=false;if(on)document.documentElement.classList.add('hw');}}catch(e){{}}}})();</script>
<title>{html.escape(t)} | Kai</title>
<meta name="description" content="{html.escape(d)}">
<meta name="keywords" content="{html.escape(KEYWORDS_RU if ru else KEYWORDS_EN)}">
<link rel="canonical" href="{self_url}">
<link rel="alternate" hreflang="ru" href="{alt_ru}"><link rel="alternate" hreflang="en" href="{alt_en}"><link rel="alternate" hreflang="x-default" href="{alt_ru}">
<meta property="og:title" content="{html.escape(t)}"><meta property="og:description" content="{html.escape(d)}"><meta property="og:image" content="{BASE}og-image.png"><meta property="og:url" content="{self_url}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap">
<style>{INDEX_CSS}/* Halloween (html.hw): та же палитра, что на главной, чате и в кабинете */
html.hw{{--bg:#0C0A0E;--bg-1:#140F13;--bg-2:#1C1518;--border:#2E201C;--ink:#FBF5EE;--text:#D9CFC8;--muted:#9A8A86;--dim:#6E5B58;--accent:#FF7A1A;--accent-2:#FFB347}}
html.hw .badge.crm{{border-color:rgba(255,122,26,.45)}}html.hw .msg.me{{background:rgba(255,122,26,.18);border-color:rgba(255,122,26,.45)}}
</style>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": t, "description": d, "url": self_url, "inLanguage": lang,
    "isPartOf": {"@type": "WebSite", "name": "Kai", "url": BASE},
    "hasPart": [{"@type": "Article", "headline": g["title_ru" if ru else "title_en"], "url": self_url + g["slug"] + ".html"} for g in guides]}, ensure_ascii=False)}</script>
</head>
<body><div class="wrap">
<header><a class="brand" href="{up}" aria-label="Kai — {'на главную' if ru else 'home'}">{MARK}<span>Kai</span></a><nav><a href="{up}#pricing">{'Тарифы' if ru else 'Plans'}</a><a href="{alt_en if ru else alt_ru}">{'EN' if ru else 'RU'}</a></nav></header>
<h1>{html.escape(t)}</h1>
<p class="lead">{html.escape(d)}</p>
<a class="card" href="{up}cases/{"" if ru else "en/"}" style="border-color:var(--accent)"><b>{"Примеры: было → стало" if ru else "Examples: before → after"}</b><span>{"Четыре ситуации в amoCRM и Kommo: воронка до, сообщение Kai, что он сделал, воронка после." if ru else "Four situations in amoCRM and Kommo: the pipeline before, the message to Kai, what it did, the pipeline after."}</span></a>
{items}
<div class="cta"><b style="color:var(--ink)">{'Хотите, чтобы это сделал Kai?' if ru else 'Want Kai to do it for you?'}</b><br>
<a href="https://t.me/aiicrm_bot">{'Попробовать в Telegram' if ru else 'Try in Telegram'}</a><a class="alt" href="{chat}">{'Открыть веб-чат' if ru else 'Open web chat'}</a></div>
<footer>© 2026 Kai · <a href="{up}privacy{'' if ru else '-en'}.html" style="color:var(--muted)">{'Конфиденциальность' if ru else 'Privacy'}</a></footer>
</div></body></html>
"""


def main() -> None:
    guides = json.load(io.open(os.path.join(HERE, "guides.json"), encoding="utf-8"))
    os.makedirs(os.path.join(HERE, "guides", "en"), exist_ok=True)
    for g in guides:
        io.open(os.path.join(HERE, "guides", f"{g['slug']}.html"), "w", encoding="utf-8", newline="\n").write(g["html_ru"])
        io.open(os.path.join(HERE, "guides", "en", f"{g['slug']}.html"), "w", encoding="utf-8", newline="\n").write(g["html_en"])
    io.open(os.path.join(HERE, "guides", "index.html"), "w", encoding="utf-8", newline="\n").write(index_page("ru", guides))
    io.open(os.path.join(HERE, "guides", "en", "index.html"), "w", encoding="utf-8", newline="\n").write(index_page("en", guides))
    # sitemap: главная, /en/, политики, гайды
    urls = [("", "1.0", "weekly"), ("en/", "0.9", "weekly"), ("guides/", "0.8", "weekly"), ("guides/en/", "0.8", "weekly"), ("cases/", "0.9", "monthly"), ("cases/en/", "0.9", "monthly")]
    urls += [(f"guides/{g['slug']}.html", "0.8", "monthly") for g in guides] + [(f"guides/en/{g['slug']}.html", "0.8", "monthly") for g in guides]
    urls += [(p, "0.3", "monthly") for p in ("privacy.html", "privacy-en.html", "terms.html", "terms-en.html", "refund.html", "refund-en.html")]
    body = "".join(f"  <url>\n    <loc>{BASE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{c}</changefreq>\n    <priority>{p}</priority>\n  </url>\n" for u, p, c in urls)
    io.open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")
    print(f"guides: {len(guides)} × 2 языка, sitemap: {len(urls)} URL")


if __name__ == "__main__":
    main()
