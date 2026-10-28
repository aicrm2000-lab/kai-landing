# -*- coding: utf-8 -*-
"""Сборка страницы «Примеры: было → стало»: cases/index.html (RU) и cases/en/index.html (EN) из cases_data.py.

Запуск: py -3.12 build_cases.py && py -3.12 build_guides.py   (sitemap добавляет cases/ сам build_guides)
Стиль — как у гайдов (те же переменные, Manrope + JetBrains Mono), без зависимостей; каждый пример: типовая картина
до, сообщение Kai, действия (настоящие имена из каталога бота), результат после, выигрыш и время."""
import datetime as dt
import html
import io
import json
import os
import re

from cases_data import ACTION_LABELS, CASES

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://aii-crm.com/"
TODAY = dt.date.today().isoformat()
MARK = ('<svg viewBox="0 0 48 48" width="28" height="28" aria-hidden="true"><path d="M39.21 19.58A15.84 15.84 0 1 1 23.5 8.17" fill="none" '
        'stroke="var(--accent)" stroke-width="6.72" stroke-linecap="round"/><circle cx="33.12" cy="11.44" r="3.36" fill="var(--accent-2)"/></svg>')
_m = re.search(r'<link rel="icon" href="([^"]+)"', io.open(os.path.join(HERE, "index.html"), encoding="utf-8").read())
FAVICON = _m.group(1) if _m else ""

CSS = """
:root{--bg:#0B0A14;--bg-1:#100E20;--bg-2:#171332;--border:#241D45;--ink:#F4F2FF;--text:#CBC5E4;--muted:#8B83AC;--accent:#7C5CFF;--accent-2:#A78BFA;--good:#43E0A0;--bad:#FF7B93;--warn:#F5C451;--mono:'JetBrains Mono',ui-monospace,monospace}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--text);font:17px/1.6 'Manrope',system-ui,sans-serif;padding:0 16px 64px}
.wrap{max-width:860px;margin:0 auto}header{display:flex;align-items:center;gap:12px;padding:22px 0;border-bottom:1px solid var(--border)}
header a{color:var(--ink);text-decoration:none;font-weight:700}header .brand{display:flex;align-items:center;gap:10px;color:var(--ink);text-decoration:none;font-weight:700}header .brand svg{flex:0 0 28px}header nav{margin-left:auto;display:flex;gap:18px;font-size:14px}header nav a{color:var(--muted);font-weight:500}
h1{font-size:clamp(28px,5vw,40px);line-height:1.15;letter-spacing:-.02em;color:var(--ink);margin:40px 0 12px;text-wrap:balance}
.lead{color:var(--text);max-width:64ch}
.toc{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 8px}.toc a{font:600 13px var(--mono);color:var(--accent-2);text-decoration:none;border:1px solid var(--border);border-radius:999px;padding:6px 12px}.toc a:hover{border-color:var(--accent)}
.case{margin-top:44px;border:1px solid var(--border);border-radius:18px;background:var(--bg-1);padding:22px;scroll-margin-top:16px}
.case .top{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px}.badge{font:600 11px var(--mono);letter-spacing:.08em;text-transform:uppercase;padding:4px 10px;border-radius:999px;border:1px solid var(--border);color:var(--muted)}.badge.crm{color:var(--accent-2);border-color:rgba(124,92,255,.45)}
.case h2{margin:0 0 6px;font-size:clamp(21px,3.2vw,26px);line-height:1.25;color:var(--ink);letter-spacing:-.01em;text-wrap:balance}
.case p{margin:6px 0}
.ba{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:16px 0}
.col{border:1px solid var(--border);border-radius:14px;padding:14px;background:var(--bg)}
.col h3{margin:0 0 10px;font:600 12px var(--mono);letter-spacing:.1em;text-transform:uppercase;display:flex;align-items:center;gap:8px}
.col.before h3{color:var(--bad)}.col.after h3{color:var(--good)}.col h3 i{width:8px;height:8px;border-radius:50%;background:currentColor;display:inline-block}
.board{display:flex;flex-wrap:wrap;gap:6px;align-items:center}.board span{font-size:13px;font-weight:600;color:var(--ink);background:var(--bg-2);border:1px solid var(--border);border-radius:8px;padding:6px 9px}.board em{font-style:normal;color:var(--muted);font-size:12px}
.col.after .board span{border-color:rgba(67,224,160,.35)}
.k{margin:12px 0 4px;font:600 11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.list{margin:0;padding:0;list-style:none;font-size:14px}.list li{padding:5px 0;border-top:1px solid var(--border);display:flex;gap:8px;align-items:baseline}.list li:first-child{border-top:0}
.list b{color:var(--ink);font-weight:600}.list small{color:var(--muted);font-size:12px}.list .stamp{font:600 10px var(--mono);color:var(--warn);border:1px solid rgba(245,196,81,.5);border-radius:6px;padding:1px 6px;white-space:nowrap}
.list.none li{color:var(--muted);font-style:italic}.list.pain li::before{content:'–';color:var(--bad)}.list.gain li::before{content:'✓';color:var(--good);font-weight:700}
.rule{display:grid;grid-template-columns:auto 1fr;gap:6px 10px;font-size:14px}.rule b{color:var(--ink);font-weight:600}.rule span::before{content:'→ ';color:var(--accent-2)}
.chat{margin:16px 0;display:grid;gap:10px}.msg{max-width:92%;border-radius:16px;padding:12px 14px;font-size:15px;line-height:1.5}
.msg.me{justify-self:end;background:rgba(124,92,255,.18);border:1px solid rgba(124,92,255,.45);color:var(--ink);border-bottom-right-radius:6px}
.msg.kai{justify-self:start;background:var(--bg-2);border:1px solid var(--border);border-bottom-left-radius:6px}.msg .who{display:block;font:600 11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}
.msg.kai .ok{color:var(--good);font-weight:700}
.did{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 0}.did span{font:500 12px var(--mono);color:var(--text);background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:4px 8px}.did span b{color:var(--accent-2);font-weight:600}
.time{margin-top:14px;padding:12px 14px;border-radius:12px;background:var(--bg-2);border:1px solid var(--border);font-size:14px;color:var(--text)}
.acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}.btn{display:inline-block;padding:11px 16px;border-radius:999px;background:var(--accent);color:#fff;font-weight:700;text-decoration:none;font-size:14px}.btn.alt{background:none;border:1px solid var(--border);color:var(--accent-2)}
button.btn{cursor:pointer;border:1px solid var(--border);font:inherit;font-weight:700;font-size:14px}
.cta{margin-top:40px;padding:22px;border-radius:16px;background:var(--bg-2);border:1px solid var(--border)}.cta b{color:var(--ink)}.cta a{display:inline-block;margin:10px 10px 0 0;padding:12px 18px;border-radius:999px;background:var(--accent);color:#fff;text-decoration:none;font-weight:700}
.cta a.alt{background:none;border:1px solid var(--border);color:var(--accent-2)}footer{margin-top:40px;color:var(--muted);font-size:13px}footer a{color:var(--muted)}
.more{margin-top:28px}.more a{color:var(--accent-2)}
@media (max-width:700px){.ba{grid-template-columns:1fr}.case{padding:16px;border-radius:14px}.msg{max-width:100%}body{font-size:16px}}
"""

T = {
    "ru": {"title": "Примеры: как было в CRM и как стало после одного сообщения Kai", "h1": "Было → стало: примеры настройки amoCRM и Kommo одним сообщением",
           "desc": "Четыре типовых ситуации в amoCRM и Kommo: что было в воронке, какое сообщение написали Kai, что он сделал и как CRM выглядит после. Настоящие действия, без интегратора.",
           "lead": "Каждый пример — типовая картина, с которой приходят к Kai: воронка «на всё», поля в примечаниях, задачи по памяти. Ниже — сообщение, которое пишут Kai, что он делает в CRM и что получается. Цифр клиентов тут нет, только конфигурация и время.",
           "before": "Было", "after": "Стало", "stages": "Этапы воронки", "fields": "Поля сделки", "rules": "Правила", "pains": "Что ломалось", "gains": "Что изменилось",
           "none_fields": "полей нет — всё в примечаниях", "none_rules": "правил нет — всё по памяти", "you": "Сообщение Kai", "kai": "Kai",
           "did": "Что сделал Kai", "copy": "Скопировать сообщение", "copied": "Скопировано", "try": "Повторить у себя в чате", "tg": "Открыть в Telegram",
           "cta_b": "Хочешь так же? Напиши Kai своими словами — он уточнит детали и настроит.", "cta_tg": "Попробовать в Telegram", "cta_chat": "Открыть веб-чат",
           "keywords": "примеры настройки amoCRM, примеры настройки Kommo, воронка продаж до и после, автоматизация CRM пример, ИИ-ассистент для amoCRM, ИИ для Kommo, настройка CRM без интегратора, Kai CRM, стоматология amoCRM, недвижимость Kommo, онлайн-школа CRM",
           "more": "Пошаговые гайды по amoCRM и Kommo →", "nav_guides": "Гайды", "nav_plans": "Тарифы", "privacy": "Конфиденциальность", "toc": "Примеры"},
    "en": {"title": "Examples: the CRM before and after one message to Kai", "h1": "Before → after: amoCRM and Kommo set up with one message",
           "desc": "Four typical situations in amoCRM and Kommo: what the pipeline looked like, the message sent to Kai, what Kai did and how the CRM looks after. Real actions, no integrator.",
           "lead": "Each example is a typical picture people bring to Kai: one pipeline for everything, fields in notes, tasks from memory. Below: the message people write to Kai, what it does in the CRM and the result. No client numbers here, only the configuration and the time.",
           "before": "Before", "after": "After", "stages": "Pipeline stages", "fields": "Deal fields", "rules": "Rules", "pains": "What was breaking", "gains": "What changed",
           "none_fields": "no fields — everything in notes", "none_rules": "no rules — everything from memory", "you": "Message to Kai", "kai": "Kai",
           "did": "What Kai did", "copy": "Copy the message", "copied": "Copied", "try": "Repeat it in your chat", "tg": "Open in Telegram",
           "cta_b": "Want the same? Write to Kai in your own words — it clarifies the details and sets things up.", "cta_tg": "Try in Telegram", "cta_chat": "Open web chat",
           "keywords": "amoCRM setup examples, Kommo setup examples, sales pipeline before and after, CRM automation example, AI assistant for amoCRM, AI for Kommo, CRM setup without integrator, Kai CRM, dental clinic CRM, real estate Kommo, online school CRM",
           "more": "Step-by-step amoCRM and Kommo guides →", "nav_guides": "Guides", "nav_plans": "Plans", "privacy": "Privacy", "toc": "Examples"},
}


def e(s: str) -> str:
    return html.escape(s, quote=True)


def case_html(c: dict, lang: str) -> str:
    L = T[lang]
    b, a = c["before"], c["after"]
    stages = lambda arr: '<div class="board">' + '<em>→</em>'.join(f"<span>{e(s)}</span>" for s in arr) + "</div>"

    def fields(arr):
        if not arr:
            return f'<ul class="list none"><li>{e(L["none_fields"])}</li></ul>'
        return '<ul class="list">' + "".join(f"<li><b>{e(n)}</b>" + (f'<span class="stamp">{e(note)}</span>' if note and ("обяз" in note or "required" in note) else (f"<small>{e(note)}</small>" if note else "")) + "</li>" for n, note in arr) + "</ul>"

    def rules(arr):
        if not arr:
            return f'<ul class="list none"><li>{e(L["none_rules"])}</li></ul>'
        return '<div class="rule">' + "".join(f"<b>{e(w)}</b><span>{e(d)}</span>" for w, d in arr) + "</div>"

    pains = '<ul class="list pain">' + "".join(f"<li>{e(p)}</li>" for p in b["pains"][lang]) + "</ul>"
    gains = '<ul class="list gain">' + "".join(f"<li>{e(g)}</li>" for g in a["gains"][lang]) + "</ul>"
    did = '<div class="did">' + "".join(f"<span>{e(ACTION_LABELS[n][lang])}{f' <b>×{k}</b>' if k > 1 else ''}</span>" for n, k in c["actions"]) + "</div>"
    reply = e(c["reply"][lang]).replace("Готово.", '<span class="ok">Готово.</span>', 1).replace("Done.", '<span class="ok">Done.</span>', 1)
    chat = f"https://app.aii-crm.com/chat?lang={lang}"
    return f"""
<article class="case" id="{c['id']}">
  <div class="top"><span class="badge crm">{e(c['crm'])}</span><span class="badge">{e(c['kind'][lang])}</span></div>
  <h2>{e(c['title'][lang])}</h2>
  <p>{e(b['lead'][lang])}</p>
  <div class="ba">
    <div class="col before"><h3><i></i>{e(L['before'])}</h3>
      <div class="k">{e(L['stages'])}</div>{stages(b['stages'][lang])}
      <div class="k">{e(L['fields'])}</div>{fields(b['fields'][lang])}
      <div class="k">{e(L['rules'])}</div>{rules(b['rules'][lang])}
      <div class="k">{e(L['pains'])}</div>{pains}
    </div>
    <div class="col after"><h3><i></i>{e(L['after'])}</h3>
      <div class="k">{e(L['stages'])}</div>{stages(a['stages'][lang])}
      <div class="k">{e(L['fields'])}</div>{fields(a['fields'][lang])}
      <div class="k">{e(L['rules'])}</div>{rules(a['rules'][lang])}
      <div class="k">{e(L['gains'])}</div>{gains}
    </div>
  </div>
  <div class="chat">
    <div class="msg me"><span class="who">{e(L['you'])}</span>{e(c['message'][lang])}</div>
    <div class="msg kai"><span class="who">{e(L['kai'])}</span>{reply}</div>
  </div>
  <div class="k">{e(L['did'])}</div>{did}
  <div class="time">{e(c['time'][lang])}</div>
  <div class="acts"><button class="btn alt" type="button" data-copy="{e(c['message'][lang])}">{e(L['copy'])}</button><a class="btn" href="{chat}">{e(L['try'])}</a><a class="btn alt" href="https://t.me/aiicrm_bot" target="_blank" rel="noopener">{e(L['tg'])}</a></div>
</article>"""


def page(lang: str) -> str:
    L, ru = T[lang], lang == "ru"
    self_url = BASE + ("cases/" if ru else "cases/en/")
    alt_ru, alt_en = BASE + "cases/", BASE + "cases/en/"
    up = "../" if ru else "../../"
    guides = up + ("guides/" if ru else "guides/en/")
    chat = f"https://app.aii-crm.com/chat?lang={lang}"
    toc = '<div class="toc">' + "".join(f'<a href="#{c["id"]}">{e(c["crm"])} · {e(c["kind"][lang])}</a>' for c in CASES) + "</div>"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": L["h1"], "description": L["desc"], "url": self_url, "inLanguage": lang,
          "datePublished": "2026-10-27", "dateModified": TODAY, "author": {"@type": "Organization", "name": "Kai"}, "publisher": {"@type": "Organization", "name": "Kai", "url": BASE},
          "isPartOf": {"@type": "WebSite", "name": "Kai", "url": BASE},
          "hasPart": [{"@type": "HowTo", "name": c["title"][lang], "url": self_url + "#" + c["id"], "step": [{"@type": "HowToStep", "text": c["message"][lang]}]} for c in CASES]}
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(){{try{{var p=new URLSearchParams(location.search).get('hw'),d=new Date(),m=d.getMonth(),n=d.getDate(),on=(m===9&&n>=25)||(m===10&&n<=2),st=null;try{{st=localStorage.getItem('kai_hw');}}catch(e){{}}try{{var ck=document.cookie.match(/(?:^|; )kai_hw=([01])/);if(ck)st=ck[1];else if(st==='0'||st==='1')document.cookie='kai_hw='+st+';max-age=31536000;path=/;SameSite=Lax'+(/(^|[.])aii-crm[.]com$/.test(location.hostname)?';domain=aii-crm.com':'');}}catch(e){{}}if(st==='0')on=false;else if(st==='1')on=true;if(p==='1')on=true;else if(p==='0')on=false;if(on)document.documentElement.classList.add('hw');}}catch(e){{}}}})();</script>
<title>{e(L['title'])} | Kai</title>
<meta name="description" content="{e(L['desc'])}">
<meta name="keywords" content="{e(L['keywords'])}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{self_url}">
<link rel="alternate" hreflang="ru" href="{alt_ru}"><link rel="alternate" hreflang="en" href="{alt_en}"><link rel="alternate" hreflang="x-default" href="{alt_ru}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Kai"><meta property="og:url" content="{self_url}">
<meta property="og:title" content="{e(L['h1'])}"><meta property="og:description" content="{e(L['desc'])}"><meta property="og:image" content="{BASE}og-image-v5.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(L['h1'])}"><meta name="twitter:description" content="{e(L['desc'])}"><meta name="twitter:image" content="{BASE}og-image-v5.png">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}/* Halloween (html.hw): та же палитра, что на главной, чате и в кабинете */
html.hw{{--bg:#0C0A0E;--bg-1:#140F13;--bg-2:#1C1518;--border:#2E201C;--ink:#FBF5EE;--text:#D9CFC8;--muted:#9A8A86;--dim:#6E5B58;--accent:#FF7A1A;--accent-2:#FFB347}}
html.hw .badge.crm{{border-color:rgba(255,122,26,.45)}}html.hw .msg.me{{background:rgba(255,122,26,.18);border-color:rgba(255,122,26,.45)}}
</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body><div class="wrap">
<header><a class="brand" href="{up}" aria-label="Kai — {'на главную' if ru else 'home'}">{MARK}<span>Kai</span></a><nav><a href="{guides}">{e(L['nav_guides'])}</a><a href="{up}#pricing">{e(L['nav_plans'])}</a><a href="{alt_en if ru else alt_ru}">{'EN' if ru else 'RU'}</a></nav></header>
<h1>{e(L['h1'])}</h1>
<p class="lead">{e(L['lead'])}</p>
{toc}
{''.join(case_html(c, lang) for c in CASES)}
<p class="more"><a href="{guides}">{e(L['more'])}</a></p>
<div class="cta"><b>{e(L['cta_b'])}</b><br><a href="https://t.me/aiicrm_bot">{e(L['cta_tg'])}</a><a class="alt" href="{chat}">{e(L['cta_chat'])}</a></div>
<footer>© 2026 Kai · <a href="{up}privacy{'' if ru else '-en'}.html">{e(L['privacy'])}</a></footer>
</div>
<script>
document.querySelectorAll('[data-copy]').forEach(function(b){{ b.addEventListener('click', function(){{ var t=b.getAttribute('data-copy'), done=function(){{ var o=b.textContent; b.textContent={json.dumps(L['copied'], ensure_ascii=False)}; setTimeout(function(){{ b.textContent=o; }},1500); }};
  if(navigator.clipboard) navigator.clipboard.writeText(t).then(done); else {{ var ta=document.createElement('textarea'); ta.value=t; document.body.appendChild(ta); ta.select(); try{{document.execCommand('copy');}}catch(e){{}} ta.remove(); done(); }} }}); }});
</script>
</body></html>
"""


def main() -> None:
    os.makedirs(os.path.join(HERE, "cases", "en"), exist_ok=True)
    io.open(os.path.join(HERE, "cases", "index.html"), "w", encoding="utf-8", newline="\n").write(page("ru"))
    io.open(os.path.join(HERE, "cases", "en", "index.html"), "w", encoding="utf-8", newline="\n").write(page("en"))
    print(f"cases: {len(CASES)} × 2 языка")


if __name__ == "__main__":
    main()
