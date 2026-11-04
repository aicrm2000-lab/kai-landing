# -*- coding: utf-8 -*-
"""HubSpot на главной (04.11.2026): логотип в строке CRM с пометкой «в разработке» (ведёт на гайд), вопрос в FAQ
(видимый и JSON-LD, седьмой — после Pipedrive), featureList, ключевые слова, короткие заголовки гайда RU/EN; ссылки на
гайды в языковых версиях — на гайд того же языка. Остальные языки — переводчики.
Запуск один раз: py -3.12 i18n/tools/add_hubspot_landing.py"""
import io
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_DIR = r"C:\Users\E09A~1\AppData\Local\Temp\claude\b70d0e96dfc39538\fc072491-67b8-4412-a56a-d36714a33fc9\scratchpad\hubspot-logos\HubSpot"

Q_RU, Q_EN = "Kai работает с HubSpot?", "Does Kai work with HubSpot?"
A_RU = ("Подключение по кнопке — в разработке. Уже сейчас HubSpot подключается по API как своя CRM: ключ service key в "
        "HubSpot и готовая спецификация Kai, на тарифе Max. Kai видит воронки и сделки, создаёт сделки, контакты, задачи и заметки.")
A_EN = ("One-click connection is in development. Today HubSpot connects through the API as a custom CRM: a HubSpot service key "
        "plus Kai’s ready-made spec, on the Max plan. Kai sees pipelines and deals and creates deals, contacts, tasks and notes.")
FEAT_RU = "HubSpot по API (подключение по кнопке — в разработке)"
FEAT_EN = "HubSpot via API (one-click connection in development)"
TIP_RU = "HubSpot: подключение по API уже сейчас, по кнопке — в разработке"
TIP_EN = "HubSpot: connect via API today, one-click connection in development"


def rep(s, old, new, cnt=1):
    assert s.count(old) == cnt, (s.count(old), old[:90])
    return s.replace(old, new)


def wordmark() -> str:
    """Вордмарк HubSpot из архива Тихона: в исходнике symbol + clipPath со ссылками на несуществующие id — берём только
    контуры, цвет — currentColor (как у соседних логотипов)."""
    import re
    src = io.open(os.path.join(LOGO_DIR, "HubSpot_idHe7kSdFV_3.svg"), encoding="utf-8").read()
    shapes = re.findall(r'<(?:polygon|path)\b[^>]*/>', src)
    shapes = [re.sub(r'\s+transform="translate\(0 0\)"', "", x) for x in shapes]
    assert len(shapes) == 7, len(shapes)
    return ('<svg viewBox="0 0 585.44 165.95" fill="currentColor" aria-hidden="true">' + "".join(shapes) + "</svg>")


# ── index.html ──
p = os.path.join(HERE, "index.html")
s = io.open(p, encoding="utf-8").read()
anchor = '      <a href="https://app.aii-crm.com/docs/custom-crm?lang=ru" target="_blank" rel="noopener" class="int-logo soon own-link"'
block = ('      <a href="guides/hubspot-ai-assistant.html" class="int-logo soon hs-link"\n'
         f'         title="{TIP_RU}"\n         data-ru-title="{TIP_RU}"\n         data-en-title="{TIP_EN}"\n'
         '         data-ru-href="guides/hubspot-ai-assistant.html" data-en-href="guides/en/hubspot-ai-assistant.html">\n'
         f'        <span class="bx-row"><span class="int-logo-icon hs-mark">{wordmark()}</span><span class="sr-only">HubSpot</span></span>\n'
         '        <span class="soon-badge" data-ru="в разработке" data-en="in development">в разработке</span>\n'
         '      </a>\n')
s = rep(s, anchor, block + anchor)
css_anchor = ".int-logo-icon.pd-mark svg { height: 30px; }\n"
s = rep(s, css_anchor, css_anchor + ".int-logo-icon.hs-mark svg { height: 30px; }   /* HubSpot: вордмарк из архива Тихона */\n")
faq_anchor = ('      <div class="faq-item">\n        <button class="faq-q" data-ru="Kai работает с самописной или кастомной CRM?"')
item = ('      <div class="faq-item">\n'
        f'        <button class="faq-q" data-ru="{Q_RU}" data-en="{Q_EN}">{Q_RU}</button>\n'
        f'        <div class="faq-a"><div class="faq-a-inner" data-ru="{A_RU}" data-en="{A_EN}">{A_RU}</div></div>\n'
        '      </div>\n')
s = rep(s, faq_anchor, item + faq_anchor)
ld_anchor = '    {\n      "@type": "Question",\n      "name": "Kai работает с самописной или кастомной CRM?",'
ld_item = ('    {\n      "@type": "Question",\n      "name": ' + json.dumps(Q_RU, ensure_ascii=False) + ',\n'
           '      "acceptedAnswer": {\n        "@type": "Answer",\n        "text": ' + json.dumps(A_RU, ensure_ascii=False)
           + '\n      }\n    },\n')
s = rep(s, ld_anchor, ld_item + ld_anchor)
s = rep(s, '    "Подключение Pipedrive (бета): воронки, сделки, задачи, аналитика"\n  ],',
        '    "Подключение Pipedrive (бета): воронки, сделки, задачи, аналитика",\n    "' + FEAT_RU + '"\n  ],')
kw_start = s.index('<meta name="keywords" content="')
kw_end = s.index('">', kw_start)
s = s[:kw_end] + ", HubSpot, ИИ-ассистент для HubSpot, настройка HubSpot" + s[kw_end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ── build_en.py ──
p = os.path.join(HERE, "build_en.py")
s = io.open(p, encoding="utf-8").read()
s = rep(s, '"Pipedrive, Pipedrive AI assistant, AI for Pipedrive, Pipedrive setup"),',
        '"Pipedrive, Pipedrive AI assistant, AI for Pipedrive, Pipedrive setup, HubSpot, HubSpot AI assistant, AI for HubSpot"),')
s = rep(s, '''                    "Pipedrive connection (beta): pipelines, deals, activities, analytics"],''',
        '''                    "Pipedrive connection (beta): pipelines, deals, activities, analytics",
                    "''' + FEAT_EN + '''"],''')
s = rep(s, '''        ("Does Kai work with a custom or in-house CRM?",''',
        '''        (''' + json.dumps(Q_EN) + ''', ''' + json.dumps(A_EN, ensure_ascii=False) + '''),
        ("Does Kai work with a custom or in-house CRM?",''')
s = rep(s, '''    html = html.replace('href="../guides/"', 'href="../guides/en/"')''',
        '''    html = html.replace('href="../guides/"', 'href="../guides/en/"')
    html = re.sub(r'href="\\.\\./guides/([a-z0-9-]+\\.html)"', r'href="../guides/en/\\1"', html)   # гайд — английский''')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ── build_i18n.py: ссылка на конкретный гайд — на гайд языка страницы ──
p = os.path.join(HERE, "build_i18n.py")
s = io.open(p, encoding="utf-8").read()
s = rep(s, '''    html = html.replace('href="../guides/"', f'href="../guides/{pg}/"').replace('href="../cases/"', f'href="../cases/{pg}/"')''',
        '''    html = html.replace('href="../guides/"', f'href="../guides/{pg}/"').replace('href="../cases/"', f'href="../cases/{pg}/"')
    html = re.sub(r'href="\\.\\./guides/([a-z0-9-]+\\.html)"', lambda m: f'href="../guides/{pg}/{m.group(1)}"', html)''')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ── check_landing: +1 пункт featureList, +1 вопрос ──
p = os.path.join(HERE, "i18n", "tools", "check_landing.py")
s = io.open(p, encoding="utf-8").read()
s = rep(s, 'if len(ld.get("featureList", [])) != 9: problems.append("ld.featureList != 9")   # +Pipedrive 03.11',
        'if len(ld.get("featureList", [])) != 10: problems.append("ld.featureList != 10")   # +Pipedrive 03.11, +HubSpot 04.11')
s = rep(s, 'if len(ld.get("faq", [])) != 8 or any(len(x) != 2 for x in ld.get("faq", [])): problems.append("ld.faq != 8 pairs")',
        'if len(ld.get("faq", [])) != 9 or any(len(x) != 2 for x in ld.get("faq", [])): problems.append("ld.faq != 9 pairs")')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ── короткие заголовки гайда для выдачи ──
SEO = {
    "ru": ("guides/hubspot-ai-assistant.html", "ИИ-ассистент для HubSpot: настройка CRM по сообщению в чате | Kai",
           "Kai работает с HubSpot по API: воронки, сделки, контакты, задачи. Как подключить через service key сейчас; "
           "подключение по кнопке — в разработке."),
    "en": ("guides/en/hubspot-ai-assistant.html", "HubSpot AI assistant: set up your CRM from a chat message | Kai",
           "Kai works with HubSpot via API: pipelines, deals, contacts, tasks. Connect with a service key today; one-click "
           "connection is in development."),
}
for lang, (path, title, desc) in SEO.items():
    assert len(title) <= 70 and 70 <= len(desc) <= 158, (lang, len(title), len(desc))
    fp = os.path.join(HERE, "i18n", "seo", f"{lang}.json")
    d = json.load(io.open(fp, encoding="utf-8"))
    d[path] = {"title": title, "description": desc}
    io.open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("ok")
