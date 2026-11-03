# -*- coding: utf-8 -*-
"""Pipedrive на главной (03.11.2026): вопрос в FAQ (видимый и JSON-LD), строка в featureList, описание приложения,
ключевые слова, короткие заголовки для выдачи RU/EN. Остальные 10 языков — переводчики (i18n/<lang>.json, i18n/seo).
Запуск один раз: py -3.12 i18n/tools/add_pipedrive_landing.py"""
import io
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Q_RU = "Kai работает с Pipedrive?"
A_RU = ("Да, в бете и с тарифа Start. Подключение — ссылкой установки из Pipedrive, кнопкой «Войти через Pipedrive» в боте "
        "или личным API-токеном. Kai настраивает воронки, этапы и поля, ведёт сделки, контакты, организации, задачи и заметки "
        "и разбирает воронку. Автоматизаций по событиям для Pipedrive пока нет — они появятся после беты.")
Q_EN = "Does Kai work with Pipedrive?"
A_EN = ("Yes, in beta, from the Start plan. Connect with the install link from Pipedrive, the “Sign in with Pipedrive” button "
        "in the bot or a personal API token. Kai sets up pipelines, stages and fields, manages deals, people, organizations, "
        "activities and notes and reviews the funnel. Event automations for Pipedrive are not there yet — they come after the beta.")
FEAT_RU = "Подключение Pipedrive (бета): воронки, сделки, задачи, аналитика"
FEAT_EN = "Pipedrive connection (beta): pipelines, deals, activities, analytics"


def rep(s, old, new, cnt=1):
    assert s.count(old) == cnt, (s.count(old), old[:90])
    return s.replace(old, new)


# ── index.html ──
p = os.path.join(HERE, "index.html")
s = io.open(p, encoding="utf-8").read()
anchor = ('      <div class="faq-item">\n        <button class="faq-q" data-ru="Kai работает с самописной или кастомной CRM?"')
item = ('      <div class="faq-item">\n'
        f'        <button class="faq-q" data-ru="{Q_RU}" data-en="{Q_EN}">{Q_RU}</button>\n'
        f'        <div class="faq-a"><div class="faq-a-inner" data-ru="{A_RU}" data-en="{A_EN}">{A_RU}</div></div>\n'
        '      </div>\n')
s = rep(s, anchor, item + anchor)
# JSON-LD FAQ: новый вопрос перед «самописной CRM» (шестым — языковые версии подставляют переводы по порядку)
ld_anchor = '    {\n      "@type": "Question",\n      "name": "Kai работает с самописной или кастомной CRM?",'
ld_item = ('    {\n      "@type": "Question",\n      "name": ' + json.dumps(Q_RU, ensure_ascii=False) + ',\n'
           '      "acceptedAnswer": {\n        "@type": "Answer",\n        "text": ' + json.dumps(A_RU, ensure_ascii=False)
           + '\n      }\n    },\n')
s = rep(s, ld_anchor, ld_item + ld_anchor)
s = rep(s, '    "Подключение своей (самописной) CRM по REST API: OAuth 2.0, API-ключ, bearer"\n  ],',
        '    "Подключение своей (самописной) CRM по REST API: OAuth 2.0, API-ключ, bearer",\n    "' + FEAT_RU + '"\n  ],')
s = rep(s, "в Telegram или в браузере: amoCRM, Kommo, Bitrix24 или своя самописная CRM по API. 65 действий",
        "в Telegram или в браузере: amoCRM, Kommo, Bitrix24, Pipedrive или своя самописная CRM по API. 65 действий")
kw_start = s.index('<meta name="keywords" content="')
kw_end = s.index('">', kw_start)
s = s[:kw_end] + ", Pipedrive, ИИ-ассистент для Pipedrive, настройка Pipedrive, Pipedrive без программиста" + s[kw_end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ── build_en.py ──
p = os.path.join(HERE, "build_en.py")
s = io.open(p, encoding="utf-8").read()
s = rep(s, '"connect AI agent to custom CRM, AI assistant for in-house CRM, CRM REST API AI integration, bespoke CRM AI agent"),',
        '"connect AI agent to custom CRM, AI assistant for in-house CRM, CRM REST API AI integration, bespoke CRM AI agent, "\n'
        '                 "Pipedrive, Pipedrive AI assistant, AI for Pipedrive, Pipedrive setup"),')
s = rep(s, '''    "description": ("AI assistant that sets up your CRM from a chat message — in Telegram or in your browser: amoCRM, Kommo, "
                    "Bitrix24 or your own custom CRM via its API.''',
        '''    "description": ("AI assistant that sets up your CRM from a chat message — in Telegram or in your browser: amoCRM, Kommo, "
                    "Bitrix24, Pipedrive or your own custom CRM via its API.''')
s = rep(s, '''                    "Your own (custom, in-house) CRM via REST API: OAuth 2.0, API key, bearer"],''',
        '''                    "Your own (custom, in-house) CRM via REST API: OAuth 2.0, API key, bearer",
                    "''' + FEAT_EN + '''"],''')
s = rep(s, '''        ("Does Kai work with a custom or in-house CRM?",''',
        '''        (''' + json.dumps(Q_EN) + ''', ''' + json.dumps(A_EN, ensure_ascii=False) + '''),
        ("Does Kai work with a custom or in-house CRM?",''')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ── короткие заголовки для выдачи (главная) ──
SEO = {
    "ru": ("", "AI-ассистент для amoCRM, Kommo, Bitrix24, Pipedrive и своей CRM | Kai",
           "Kai настраивает CRM по сообщению в чате: amoCRM, Kommo, Bitrix24, Pipedrive или свою CRM по API. "
           "Воронки, поля, задачи, автоматизации. 3 дня триала."),
    "en": ("en/", "AI assistant for amoCRM, Kommo, Bitrix24, Pipedrive, custom CRM | Kai",
           "Kai sets up your CRM from a chat message: amoCRM, Kommo, Bitrix24, Pipedrive or your own CRM via API. "
           "Pipelines, fields, tasks, automations. 3-day trial."),
}
for lang, (path, title, desc) in SEO.items():
    assert len(title) <= 70 and 25 <= len(desc) <= 160, (lang, len(title), len(desc))
    fp = os.path.join(HERE, "i18n", "seo", f"{lang}.json")
    d = json.load(io.open(fp, encoding="utf-8"))
    d[path] = {"title": title, "description": desc}
    io.open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("ok")
