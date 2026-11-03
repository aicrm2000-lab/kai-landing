# -*- coding: utf-8 -*-
"""Гайд «ИИ-ассистент для Pipedrive» (03.11.2026) → guides.json (RU + EN). Оформление, шапка, сезонный скрипт и стили
берутся из гайда про Bitrix24 — меняются только мета, статья и JSON-LD. Факты — из кода бота (services/pipedrive.py,
services/crm/pipedrive_provider.py, /install/pipedrive, billing). Запуск один раз: py -3.12 i18n/tools/add_pipedrive_guide.py"""
import io
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLUG = "pipedrive-ai-assistant"
DATE = "2026-11-03"
INSTALL = "https://app.aii-crm.com/install/pipedrive"

T = {
    "ru": {
        "title": "ИИ-ассистент для Pipedrive: настройка CRM по сообщению в чате",
        "desc": ("Как ИИ-ассистент Kai настраивает Pipedrive по сообщению в чате: воронки, этапы, поля, сделки, контакты, "
                 "задачи и аналитика. Подключение по ссылке, что работает в бете и чего пока нет."),
        "og": ("Kai ставится в Pipedrive по ссылке и настраивает воронки, поля, сделки и задачи по сообщению в Telegram или "
               "в браузере. Что работает в бете, чего пока нет, сколько стоит."),
        "keywords": "ИИ-ассистент для Pipedrive, настройка Pipedrive без программиста, Pipedrive ИИ",
        "author": "Команда Kai", "home": "Kai — на главную", "nav": "Навигация", "site": "Сайт", "bot": "Telegram-бот",
        "other": "EN", "other_lang": "en", "crumbs": "Хлебные крошки", "guides": "Гайды", "crumb": "Pipedrive через ИИ",
        "guides_url": "https://aii-crm.com/guides/", "chat": "https://app.aii-crm.com/chat?lang=ru",
        "footer": ('© 2026 Kai · <a href="https://aii-crm.com/">Главная</a> · <a href="https://aii-crm.com/privacy.html">'
                   'Конфиденциальность</a> · <a href="https://aii-crm.com/terms.html">Условия</a> · '
                   '<a href="https://aii-crm.com/guides/en/pipedrive-ai-assistant.html">English version</a>'),
        "breadcrumb_guides": "Гайды",
    },
    "en": {
        "title": "Pipedrive AI assistant: set up your CRM from a chat message",
        "desc": ("How the Kai AI assistant sets up Pipedrive from a chat message: pipelines, stages, fields, deals, people, "
                 "activities and analytics. Install link, what works in the beta, what does not yet."),
        "og": ("Kai installs into Pipedrive from a link and sets up pipelines, fields, deals and activities from a message in "
               "Telegram or the browser. What works in the beta, what does not yet, pricing."),
        "keywords": "Pipedrive AI assistant, AI for Pipedrive setup, set up Pipedrive without a developer",
        "author": "Kai Team", "home": "Kai — home", "nav": "Navigation", "site": "Website", "bot": "Telegram bot",
        "other": "RU", "other_lang": "ru", "crumbs": "Breadcrumbs", "guides": "Guides", "crumb": "Pipedrive AI assistant",
        "guides_url": "https://aii-crm.com/guides/en/", "chat": "https://app.aii-crm.com/chat?lang=en",
        "footer": ('© 2026 Kai · <a href="https://aii-crm.com/">Home</a> · <a href="https://aii-crm.com/privacy-en.html">'
                   'Privacy</a> · <a href="https://aii-crm.com/terms-en.html">Terms</a> · '
                   '<a href="https://aii-crm.com/guides/pipedrive-ai-assistant.html">Русская версия</a>'),
        "breadcrumb_guides": "Guides",
    },
}

FAQ = {
    "ru": [
        ("Есть ли ИИ-ассистент, который настраивает Pipedrive по сообщению?",
         "Да, Kai. Ты описываешь процесс продаж обычными словами в Telegram или в браузере, а Kai создаёт в Pipedrive "
         "воронки и этапы, поля, сделки, контакты, организации, задачи и заметки через официальный API и разбирает воронку. "
         "Поддержка Pipedrive — в бете."),
        ("Как подключить Pipedrive к Kai?",
         "Открой ссылку установки app.aii-crm.com/install/pipedrive, разреши доступ в Pipedrive и на странице «Kai установлен» "
         "нажми «Открыть Kai в Telegram» или «Продолжить в браузере». Ещё два способа — в боте: /connect → Pipedrive (бета) → "
         "«Войти через Pipedrive» или личный API-токен из настроек Pipedrive."),
        ("Kai умеет автоматизации в Pipedrive?",
         "Пока нет. Правила на событиях Pipedrive (сделка перешла на этап → задача или уведомление) и интеграции по событиям "
         "появятся после беты. Сейчас Kai настраивает структуру, ведёт данные и задачи и разбирает воронку."),
        ("С какого тарифа доступен Pipedrive?",
         "С тарифа Start, €29 в месяц за одну CRM. Первые 3 дня — триал без карты, этого хватает, чтобы проверить Kai на своей "
         "компании в Pipedrive."),
    ],
    "en": [
        ("Is there an AI assistant that sets up Pipedrive from a chat message?",
         "Yes, Kai. You describe your sales process in plain words in Telegram or the browser, and Kai creates pipelines and "
         "stages, fields, deals, people, organizations, activities and notes in Pipedrive through the official API and reviews "
         "the funnel. Pipedrive support is in beta."),
        ("How do I connect Pipedrive to Kai?",
         "Open the install link app.aii-crm.com/install/pipedrive, allow access in Pipedrive and on the \"Kai is installed\" "
         "page press \"Open Kai in Telegram\" or \"Continue in the browser\". Two more ways in the bot: /connect → Pipedrive "
         "(beta) → \"Sign in with Pipedrive\", or a personal API token from your Pipedrive settings."),
        ("Can Kai build automations in Pipedrive?",
         "Not yet. Rules on Pipedrive events (a deal moves to a stage → a task or a notification) and event-driven "
         "integrations come after the beta. Today Kai sets up the structure, manages data and activities and reviews the funnel."),
        ("Which plan do I need for Pipedrive?",
         "Any plan from Start, €29 per month for one CRM. The first 3 days are a trial without a card, enough to test Kai on "
         "your own Pipedrive company."),
    ],
}

BODY = {
    "ru": f"""<h1>{{TITLE}}</h1>
<p class="meta">Обновлено 3 ноября 2026 · Команда Kai · 5 минут чтения</p>

<p class="lead">ИИ-ассистент для Pipedrive — это чат, в котором ты описываешь процесс продаж обычными словами, а он собирает его в Pipedrive через официальный API: воронки и этапы, поля, сделки, контакты, организации, задачи и заметки. Kai делает это в Telegram или в браузере. Поддержка Pipedrive в бете: структура, данные, задачи и аналитика работают, автоматизации на событиях Pipedrive — следующим шагом.</p>

<section class="tldr" aria-label="Коротко">
  <h2>Коротко</h2>
  <ul>
    <li>Установка — по ссылке <a href="{INSTALL}">app.aii-crm.com/install/pipedrive</a>: Pipedrive спросит разрешение, потом Kai привяжет компанию к твоему аккаунту в Telegram или в веб-чате.</li>
    <li>Работает: воронки и этапы, поля сделок, контактов и организаций со списками вариантов, сделки, контакты, организации, задачи, заметки, пользователи, аналитика воронки с выигранными и проигранными.</li>
    <li>Пока нет: правил на событиях Pipedrive (автоматизаций и интеграций Kai) и кнопок или панелей внутри Pipedrive.</li>
    <li>Доступно с тарифа Start, €29 в месяц. Первые 3 дня — триал.</li>
  </ul>
</section>

<h2>Как подключить Pipedrive к Kai</h2>
<ol>
  <li>Открой <a href="{INSTALL}">ссылку установки</a> и войди в Pipedrive, если он попросит.</li>
  <li>Pipedrive покажет, к каким данным Kai просит доступ. Нажми «Разрешить».</li>
  <li>На странице «Kai установлен в Pipedrive» нажми «Открыть Kai в Telegram» или «Продолжить в браузере». Ссылка срабатывает один раз и живёт 30 минут: она привязывает эту компанию Pipedrive к твоему аккаунту Kai.</li>
  <li>Kai подтвердит подключение и спросит, что настраиваем.</li>
</ol>
<p>Ещё два способа — прямо в боте <a href="https://t.me/aiicrm_bot">@aiicrm_bot</a> или в <a href="https://app.aii-crm.com/chat?lang=ru">веб-чате</a>: команда <kbd>/connect</kbd> → «Pipedrive (бета)» → «Войти через Pipedrive», или пришли личный API-токен: Pipedrive → аватар → «Личные настройки» → вкладка API.</p>
<div class="note warn">Вход через Pipedrive идёт по OAuth: пароль от Pipedrive Kai не видит. API-токен действует от твоего имени — не публикуй его. Перевыпустишь токен в тех же настройках — старый перестанет работать.</div>

<h2>Что Kai настраивает в Pipedrive</h2>
<ul>
  <li><strong>Воронки и этапы.</strong> Новая воронка с этапами одним сообщением; добавить, переименовать или удалить этап.</li>
  <li><strong>Поля.</strong> Свои поля в сделках, контактах и организациях, включая списки вариантов, и их значения в сделке.</li>
  <li><strong>Сделки.</strong> Создать, передвинуть по этапам, поменять сумму и ответственного, найти; ссылка на карточку сделки в Pipedrive.</li>
  <li><strong>Контакты и организации.</strong> Создать и привязать к сделке.</li>
  <li><strong>Задачи и заметки.</strong> Задача со сроком по сделке и заметка прямо из чата.</li>
  <li><strong>Аналитика воронки.</strong> Сколько сделок на каждом этапе, сколько выиграно и проиграно, «здоровье» конкретной сделки.</li>
</ul>
<p>Все действия идут через официальный API Pipedrive. Всё созданное остаётся в твоей компании Pipedrive, даже если ты перестанешь пользоваться ассистентом.</p>

<h2>Чего Kai в Pipedrive пока не делает</h2>
<div class="table-wrap">
<table>
  <thead><tr><th>Задача</th><th>Статус в Kai</th><th>Что делать сейчас</th></tr></thead>
  <tbody>
    <tr><td>Правила на событиях: сделка перешла на этап → задача, уведомление</td><td>После беты</td><td>Встроенные автоматизации Pipedrive, если они есть в твоём тарифе Pipedrive.</td></tr>
    <tr><td>Интеграции с другими сервисами по событиям</td><td>После беты</td><td>Приложения из маркетплейса Pipedrive или разработчик.</td></tr>
    <tr><td>Кнопки и панели Kai внутри Pipedrive</td><td>Пока нет</td><td>Работай с Kai в чате: в Telegram или в браузере.</td></tr>
  </tbody>
</table>
</div>
<p>Честный итог: сегодня Kai для Pipedrive — это настройка структуры, порядок в данных, задачи и разбор воронки. Автоматизации по событиям уже работают для amoCRM и Kommo и придут в Pipedrive после беты.</p>

<h2>С Kai это одно сообщение</h2>
<p>Ты описываешь бизнес, Kai задаёт уточняющие вопросы, показывает план, после подтверждения создаёт всё через API и присылает отчёт. Примеры:</p>
<pre>Создай в Pipedrive воронку для B2B-продаж: Новый лид → Квалификация → Демо → КП → Переговоры → Договор. Добавь в сделки числовое поле «Бюджет» и список «Источник» с вариантами Сайт, Рекомендация, Выставка.</pre>
<pre>Передвинь сделку «Альфа, 20 мест» на этап Переговоры и добавь заметку: просили годовой счёт.</pre>
<pre>Сколько сделок на каждом этапе воронки и сколько выиграно и проиграно?</pre>
<p>Тарифы те же, что для других CRM: Start €29 в месяц за одну CRM, Pro €59 до трёх CRM, Max €119 до десяти. Первые 3 дня — триал без карты, около 25 запросов на функциях Start. Kai говорит по-русски и по-английски.</p>

<h2>Частые вопросы</h2>
<div class="faq">
{{FAQ}}
</div>

<h2>Что дальше</h2>
<p>Открой ссылку установки, разреши доступ и попроси Kai показать воронки — так за минуту видно, что ассистент работает с твоей компанией.</p>
<div class="cta">
  <a class="btn btn-primary" href="{INSTALL}">Установить Kai в Pipedrive</a>
  <a class="btn btn-secondary" href="https://app.aii-crm.com/chat?lang=ru">Открыть веб-чат</a>
</div>

<p class="author">Автор: Команда Kai · Обновлено <time datetime="{DATE}">3 ноября 2026</time> · Возможности и ограничения описаны по состоянию на дату публикации, актуальный статус Kai сообщает в чате.</p>""",
    "en": f"""<h1>{{TITLE}}</h1>
<p class="meta">Updated November 3, 2026 · Kai Team · 5 min read</p>

<p class="lead">An AI assistant for Pipedrive is a chat where you describe your sales process in plain words and it builds it in Pipedrive through the official API: pipelines and stages, fields, deals, people, organizations, activities and notes. Kai does this in Telegram or in the browser. Pipedrive support is in beta: structure, data, activities and analytics work; automations on Pipedrive events come next.</p>

<section class="tldr" aria-label="TL;DR">
  <h2>TL;DR</h2>
  <ul>
    <li>Install from the link <a href="{INSTALL}">app.aii-crm.com/install/pipedrive</a>: Pipedrive asks for permission, then Kai links the company to your account in Telegram or the web chat.</li>
    <li>Works: pipelines and stages, deal, person and organization fields with option lists, deals, people, organizations, activities, notes, users, funnel analytics with won and lost deals.</li>
    <li>Not yet: rules on Pipedrive events (Kai's automations and integrations) and buttons or panels inside Pipedrive.</li>
    <li>Available from the Start plan, €29 per month. The first 3 days are a trial.</li>
  </ul>
</section>

<h2>How to connect Pipedrive to Kai</h2>
<ol>
  <li>Open the <a href="{INSTALL}">install link</a> and sign in to Pipedrive if it asks.</li>
  <li>Pipedrive shows which data Kai asks to access. Press Allow.</li>
  <li>On the "Kai is installed in Pipedrive" page press "Open Kai in Telegram" or "Continue in the browser". The link works once, for 30 minutes: it ties this Pipedrive company to your Kai account.</li>
  <li>Kai confirms the connection and asks what to set up.</li>
</ol>
<p>Two more ways, right in the bot <a href="https://t.me/aiicrm_bot">@aiicrm_bot</a> or the <a href="https://app.aii-crm.com/chat?lang=en">web chat</a>: the <kbd>/connect</kbd> command → "Pipedrive (beta)" → "Sign in with Pipedrive", or send a personal API token: Pipedrive → avatar → Personal preferences → API tab.</p>
<div class="note warn">Signing in with Pipedrive uses OAuth: Kai never sees your Pipedrive password. An API token acts on your behalf, so do not publish it. Regenerate it in the same settings and the old one stops working.</div>

<h2>What Kai sets up in Pipedrive</h2>
<ul>
  <li><strong>Pipelines and stages.</strong> A new pipeline with stages from one message; add, rename or delete a stage.</li>
  <li><strong>Fields.</strong> Custom fields on deals, people and organizations, including option lists, and their values on a deal.</li>
  <li><strong>Deals.</strong> Create, move between stages, change the value and the owner, search; a link to the deal card in Pipedrive.</li>
  <li><strong>People and organizations.</strong> Create them and link them to a deal.</li>
  <li><strong>Activities and notes.</strong> An activity with a due date on a deal and a note, straight from the chat.</li>
  <li><strong>Funnel analytics.</strong> Deals per stage, won and lost deals, the "health" of a specific deal.</li>
</ul>
<p>Every action goes through the official Pipedrive API. Everything created stays in your Pipedrive company whether or not you keep using the assistant.</p>

<h2>What Kai does not do in Pipedrive yet</h2>
<div class="table-wrap">
<table>
  <thead><tr><th>Job</th><th>Status in Kai</th><th>What to do now</th></tr></thead>
  <tbody>
    <tr><td>Rules on events: a deal moves to a stage → an activity, a notification</td><td>After the beta</td><td>Pipedrive's built-in automations, if your Pipedrive plan has them.</td></tr>
    <tr><td>Event-driven integrations with other services</td><td>After the beta</td><td>Apps from the Pipedrive Marketplace or a developer.</td></tr>
    <tr><td>Kai buttons and panels inside Pipedrive</td><td>Not yet</td><td>Work with Kai in the chat: in Telegram or in the browser.</td></tr>
  </tbody>
</table>
</div>
<p>The honest summary: today Kai for Pipedrive sets up the structure, keeps the data in order, handles activities and reviews the funnel. Event automations already work for amoCRM and Kommo and come to Pipedrive after the beta.</p>

<h2>With Kai it is one message</h2>
<p>You describe the business, Kai asks clarifying questions, shows a plan, creates everything through the API once you confirm and sends a report. Examples:</p>
<pre>Create a Pipedrive pipeline for B2B sales: New lead → Qualified → Demo → Proposal → Negotiation → Contract. Add a number field Budget to deals and a list field Source with Website, Referral, Event.</pre>
<pre>Move the deal "Alpha, 20 seats" to Negotiation and add a note: they asked for an annual invoice.</pre>
<pre>How many deals are at each stage of the pipeline, and how many are won and lost?</pre>
<p>Plans are the same as for the other CRMs: Start €29 per month for one CRM, Pro €59 for up to three CRMs, Max €119 for up to ten. The first 3 days are a trial, no card, about 25 requests on Start features. Kai speaks English and Russian.</p>

<h2>FAQ</h2>
<div class="faq">
{{FAQ}}
</div>

<h2>What next</h2>
<p>Open the install link, allow access and ask Kai to show your pipelines: in a minute you see the assistant working with your company.</p>
<div class="cta">
  <a class="btn btn-primary" href="{INSTALL}">Install Kai in Pipedrive</a>
  <a class="btn btn-secondary" href="https://app.aii-crm.com/chat?lang=en">Open web chat</a>
</div>

<p class="author">Author: Kai Team · Updated <time datetime="{DATE}">November 3, 2026</time> · Capabilities and limits are described as of the publication date; Kai reports the current status in the chat.</p>""",
}


def page(lang: str, template: str) -> str:
    t = T[lang]
    other = "en" if lang == "ru" else "ru"
    url = f"https://aii-crm.com/guides/{SLUG}.html" if lang == "ru" else f"https://aii-crm.com/guides/en/{SLUG}.html"
    ru_url, en_url = f"https://aii-crm.com/guides/{SLUG}.html", f"https://aii-crm.com/guides/en/{SLUG}.html"
    head = (f'<title>{t["title"]} | Kai</title>\n'
            f'<meta name="description" content="{t["desc"]}">\n'
            f'<meta name="keywords" content="{t["keywords"]}">\n'
            '<meta name="robots" content="index, follow">\n'
            f'<meta name="author" content="{t["author"]}">\n'
            f'<link rel="canonical" href="{url}">\n'
            f'<link rel="alternate" hreflang="ru" href="{ru_url}">\n'
            f'<link rel="alternate" hreflang="en" href="{en_url}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{ru_url}">\n'
            '<meta property="og:type" content="article">\n'
            f'<meta property="og:locale" content="{"ru_RU" if lang == "ru" else "en_US"}">\n'
            f'<meta property="og:locale:alternate" content="{"en_US" if lang == "ru" else "ru_RU"}">\n'
            '<meta property="og:site_name" content="Kai">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:title" content="{t["title"]}">\n'
            f'<meta property="og:description" content="{t["og"]}">\n'
            '<meta property="og:image" content="https://aii-crm.com/og-image-v5.png">\n'
            f'<meta property="article:published_time" content="{DATE}">\n'
            f'<meta property="article:modified_time" content="{DATE}">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{t["title"]}">\n'
            f'<meta name="twitter:description" content="{t["og"]}">\n'
            '<meta name="twitter:image" content="https://aii-crm.com/og-image-v5.png">\n')
    faq_html = "\n".join(f'  <div class="faq-item">\n    <h3>{q}</h3>\n    <p>{a}</p>\n  </div>' for q, a in FAQ[lang])
    body = BODY[lang].replace("{TITLE}", t["title"]).replace("{FAQ}", faq_html)
    other_url = en_url if lang == "ru" else ru_url
    header = (f'<header class="header">\n  <div class="header-in">\n    <a class="brand" href="https://aii-crm.com/" aria-label="{t["home"]}">\n'
              '      <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M39.21 19.58A15.84 15.84 0 1 1 23.5 8.17" fill="none" '
              'stroke="var(--accent)" stroke-width="6.72" stroke-linecap="round"/><circle cx="33.12" cy="11.44" r="3.36" '
              'fill="var(--accent-2)"/></svg>\n      Kai\n    </a>\n'
              f'    <nav class="nav" aria-label="{t["nav"]}">\n      <a href="https://aii-crm.com/">{t["site"]}</a>\n'
              f'      <a href="https://t.me/aiicrm_bot">{t["bot"]}</a>\n'
              f'      <a href="{other_url}" hreflang="{other}">{t["other"]}</a>\n    </nav>\n  </div>\n</header>\n\n<main>\n<article>\n'
              f'<nav class="crumbs" aria-label="{t["crumbs"]}">\n  <a href="https://aii-crm.com/">Kai</a> › '
              f'<a href="{t["guides_url"]}">{t["guides"]}</a> › {t["crumb"]}\n</nav>\n\n')
    main = header + body + "\n</article>\n</main>\n\n<footer>\n  " + t["footer"] + "\n</footer>\n\n"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": url + "#article", "headline": t["title"], "description": t["desc"], "inLanguage": lang,
         "datePublished": DATE, "dateModified": DATE, "mainEntityOfPage": url, "image": "https://aii-crm.com/og-image-v5.png",
         "author": {"@type": "Organization", "name": "Kai", "url": "https://aii-crm.com/"},
         "publisher": {"@type": "Organization", "name": "Kai", "url": "https://aii-crm.com/"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                                            for q, a in FAQ[lang]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Kai", "item": "https://aii-crm.com/"},
            {"@type": "ListItem", "position": 2, "name": t["breadcrumb_guides"], "item": "https://aii-crm.com/guides/"},
            {"@type": "ListItem", "position": 3, "name": t["title"], "item": url}]}]}
    ld_html = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + "\n</script>\n"
    # из шаблона: всё до <title> (сезонный скрипт, viewport, иконки), стили, закрытие head
    pre = template[:template.index("<title>")]
    styles = template[template.index('<link rel="preconnect"'):template.index("</head>")]
    return pre + head + styles + "</head>\n<body>\n" + main + ld_html + "</body>\n</html>\n"


def main():
    p = os.path.join(HERE, "guides.json")
    g = json.load(io.open(p, encoding="utf-8"))
    assert not any(x["slug"] == SLUG for x in g), "гайд уже есть"
    b = next(x for x in g if x["slug"] == "bitrix24-ai-assistant")
    g.append({"slug": SLUG, "title_ru": T["ru"]["title"], "title_en": T["en"]["title"],
              "desc_ru": T["ru"]["desc"], "desc_en": T["en"]["desc"],
              "html_ru": page("ru", b["html_ru"]), "html_en": page("en", b["html_en"]),
              "prompts": ["ИИ-ассистент для Pipedrive", "настройка Pipedrive без программиста",
                          "Pipedrive AI assistant", "AI for Pipedrive setup"]})
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(g, ensure_ascii=False, indent=1))
    print("ok", len(g))


if __name__ == "__main__":
    main()
