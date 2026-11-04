# -*- coding: utf-8 -*-
"""Гайд «ИИ-ассистент для HubSpot» (04.11.2026) → guides.json (RU + EN). Оформление — из гайда про Bitrix24 (как у
Pipedrive), меняются мета, статья и JSON-LD. Факты: HubSpot сейчас подключается как своя CRM по API (готовая спецификация
services/custom_crm.EXAMPLE_SPECS["hubspot"], service key, тариф Max); подключение по кнопке — в разработке.
Запуск один раз: py -3.12 i18n/tools/add_hubspot_guide.py"""
import io
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLUG = "hubspot-ai-assistant"
DATE = "2026-11-04"
DOCS = {"ru": "https://app.aii-crm.com/docs/custom-crm?lang=ru", "en": "https://app.aii-crm.com/docs/custom-crm?lang=en"}

T = {
    "ru": {
        "title": "ИИ-ассистент для HubSpot: настройка CRM по сообщению в чате",
        "desc": ("Как подключить HubSpot к ИИ-ассистенту Kai уже сейчас — по API через service key — и что он делает в HubSpot: "
                 "воронки, сделки, контакты, задачи, заметки. Подключение по кнопке — в разработке."),
        "og": ("Kai работает с HubSpot по API: воронки, сделки, контакты, задачи и заметки по сообщению в Telegram или в браузере. "
               "Как подключить сейчас и что в разработке."),
        "keywords": "ИИ-ассистент для HubSpot, HubSpot ИИ, настройка HubSpot без программиста",
        "author": "Команда Kai", "home": "Kai — на главную", "nav": "Навигация", "site": "Сайт", "bot": "Telegram-бот",
        "other": "EN", "crumbs": "Хлебные крошки", "guides": "Гайды", "crumb": "HubSpot через ИИ",
        "guides_url": "https://aii-crm.com/guides/",
        "footer": ('© 2026 Kai · <a href="https://aii-crm.com/">Главная</a> · <a href="https://aii-crm.com/privacy.html">'
                   'Конфиденциальность</a> · <a href="https://aii-crm.com/terms.html">Условия</a> · '
                   '<a href="https://aii-crm.com/guides/en/hubspot-ai-assistant.html">English version</a>'),
        "breadcrumb_guides": "Гайды",
    },
    "en": {
        "title": "HubSpot AI assistant: set up your CRM from a chat message",
        "desc": ("How to connect HubSpot to the Kai AI assistant today, through the API with a service key, and what it does in "
                 "HubSpot: pipelines, deals, contacts, tasks, notes. One-click connection is in development."),
        "og": ("Kai works with HubSpot through the API: pipelines, deals, contacts, tasks and notes from a message in Telegram or "
               "the browser. How to connect today and what is in development."),
        "keywords": "HubSpot AI assistant, AI for HubSpot, set up HubSpot without a developer",
        "author": "Kai Team", "home": "Kai — home", "nav": "Navigation", "site": "Website", "bot": "Telegram bot",
        "other": "RU", "crumbs": "Breadcrumbs", "guides": "Guides", "crumb": "HubSpot AI assistant",
        "guides_url": "https://aii-crm.com/guides/en/",
        "footer": ('© 2026 Kai · <a href="https://aii-crm.com/">Home</a> · <a href="https://aii-crm.com/privacy-en.html">'
                   'Privacy</a> · <a href="https://aii-crm.com/terms-en.html">Terms</a> · '
                   '<a href="https://aii-crm.com/guides/hubspot-ai-assistant.html">Русская версия</a>'),
        "breadcrumb_guides": "Guides",
    },
}

FAQ = {
    "ru": [
        ("Есть ли ИИ-ассистент, который работает с HubSpot по сообщению?",
         "Да, Kai. Уже сейчас он подключается к HubSpot по API как своя CRM: видит воронки и сделки, создаёт сделки, контакты, "
         "задачи и заметки, передвигает сделки по этапам и разбирает воронку. Подключение по кнопке — в разработке."),
        ("Как подключить HubSpot к Kai сейчас?",
         "Создай в HubSpot ключ: Development → Keys → Service keys, с правами на сделки и контакты. Возьми готовую спецификацию "
         "HubSpot на странице подключения своей CRM, вставь в неё ключ и пришли Kai: /connect → «Своя CRM по API». Подключение "
         "своей CRM доступно на тарифе Max."),
        ("Когда появится подключение HubSpot по кнопке?",
         "Оно в разработке: приложение Kai для HubSpot с кнопкой «Войти через HubSpot» и ссылкой установки, без ключей и JSON. "
         "Как только запустим, Kai напишет об этом в чате."),
        ("Чего Kai пока не делает в HubSpot?",
         "Не создаёт воронки и поля, не работает с компаниями и не запускает автоматизации по событиям HubSpot. Всё это "
         "запланировано вместе с подключением по кнопке."),
    ],
    "en": [
        ("Is there an AI assistant that works with HubSpot from a chat message?",
         "Yes, Kai. Today it connects to HubSpot through the API as a custom CRM: it sees pipelines and deals, creates deals, "
         "contacts, tasks and notes, moves deals between stages and reviews the funnel. One-click connection is in development."),
        ("How do I connect HubSpot to Kai today?",
         "Create a key in HubSpot: Development → Keys → Service keys, with access to deals and contacts. Take the ready-made "
         "HubSpot spec from the custom CRM page, paste the key into it and send it to Kai: /connect → \"My own CRM via API\". "
         "Connecting a custom CRM is part of the Max plan."),
        ("When will one-click HubSpot connection be available?",
         "It is in development: a Kai app for HubSpot with a \"Sign in with HubSpot\" button and an install link, with no keys "
         "or JSON. As soon as it launches, Kai will tell you in the chat."),
        ("What does Kai not do in HubSpot yet?",
         "It does not create pipelines or fields, does not work with companies and does not run automations on HubSpot events. "
         "All of this is planned together with the one-click connection."),
    ],
}

BODY = {
    "ru": """<h1>{TITLE}</h1>
<p class="meta">Обновлено 4 ноября 2026 · Команда Kai · 5 минут чтения</p>

<p class="lead">ИИ-ассистент для HubSpot — это чат, в котором ты описываешь процесс продаж обычными словами, а он работает с HubSpot через официальный API: показывает воронки и сделки, создаёт сделки, контакты, задачи и заметки и разбирает воронку. Kai делает это в Telegram или в браузере. Уже сейчас HubSpot подключается по API как своя CRM; подключение по кнопке — в разработке.</p>

<section class="tldr" aria-label="Коротко">
  <h2>Коротко</h2>
  <ul>
    <li>Сейчас: ключ service key в HubSpot плюс готовая спецификация Kai — подключение своей CRM по API, тариф Max.</li>
    <li>Работает: воронки и этапы, сделки (список, поиск, создание, смена этапа и суммы), контакты, задачи и заметки по сделке, аналитика воронки.</li>
    <li>В разработке: приложение Kai для HubSpot — кнопка «Войти через HubSpot» и ссылка установки, без ключей и JSON.</li>
    <li>Пока нет: создания воронок и полей, компаний, автоматизаций по событиям HubSpot.</li>
  </ul>
</section>

<h2>Как подключить HubSpot к Kai сейчас</h2>
<ol>
  <li>В HubSpot открой <kbd>Development → Keys → Service keys</kbd> и нажми <kbd>Create service key</kbd>. Создать ключ может суперадмин или пользователь с правом Developer tools.</li>
  <li>Назови ключ «Kai» и добавь права: <code>crm.objects.deals.read</code>, <code>crm.objects.deals.write</code>, <code>crm.schemas.deals.read</code>, <code>crm.objects.contacts.read</code>, <code>crm.objects.contacts.write</code>. Нажми <kbd>Create</kbd> и скопируй ключ.</li>
  <li>Открой <a href="{DOCS}">страницу подключения своей CRM</a>, раздел «Готовые спецификации: HubSpot», скопируй JSON и вставь ключ в поле <code>token</code>.</li>
  <li>В боте <a href="https://t.me/aiicrm_bot">@aiicrm_bot</a> или в <a href="https://app.aii-crm.com/chat?lang=ru">веб-чате</a>: <kbd>/connect</kbd> → «Своя CRM по API» → вставь JSON. Kai проверит доступ и покажет воронки сделок.</li>
</ol>
<div class="note warn">Ключ service key действует от имени аккаунта HubSpot — не публикуй его. В HubSpot его можно перевыпустить или удалить, тогда старый перестанет работать.</div>

<h2>Что Kai делает в HubSpot</h2>
<ul>
  <li><strong>Воронки и этапы.</strong> Показывает воронки сделок и этапы, считает сделки по этапам.</li>
  <li><strong>Сделки.</strong> Находит сделку по названию, создаёт новую в нужной воронке и на нужном этапе, меняет этап и сумму.</li>
  <li><strong>Контакты.</strong> Создаёт контакт с телефоном и почтой.</li>
  <li><strong>Задачи и заметки.</strong> Ставит задачу со сроком и добавляет заметку к сделке.</li>
  <li><strong>Аналитика.</strong> Сколько сделок на каждом этапе воронки.</li>
</ul>
<p>Все действия идут через официальный API HubSpot. Всё созданное остаётся в твоём аккаунте HubSpot, даже если ты перестанешь пользоваться ассистентом.</p>

<h2>Что в разработке и чего пока нет</h2>
<div class="table-wrap">
<table>
  <thead><tr><th>Задача</th><th>Статус в Kai</th><th>Что делать сейчас</th></tr></thead>
  <tbody>
    <tr><td>Подключение по кнопке «Войти через HubSpot»</td><td>В разработке</td><td>Подключить по API через service key.</td></tr>
    <tr><td>Создание воронок, этапов и полей из чата</td><td>Пока нет</td><td>Настроить в HubSpot вручную; Kai подскажет структуру и составит ТЗ.</td></tr>
    <tr><td>Компании</td><td>Пока нет</td><td>Работать с компаниями в HubSpot.</td></tr>
    <tr><td>Автоматизации по событиям HubSpot</td><td>Пока нет</td><td>Встроенные workflows HubSpot, если они есть в твоём тарифе HubSpot.</td></tr>
  </tbody>
</table>
</div>

<h2>С Kai это одно сообщение</h2>
<p>После подключения просишь Kai о том же, о чём просил бы с любой CRM. Примеры:</p>
<pre>Покажи воронки и сколько сделок на каждом этапе.</pre>
<pre>Создай сделку «Альфа, 20 мест» на 12000 в воронке Sales Pipeline.</pre>
<pre>Поставь задачу «перезвонить» по сделке «Альфа, 20 мест» на завтра и добавь заметку: просили годовой счёт.</pre>
<p>Подключение своей CRM по API, в том числе HubSpot, — на тарифе Max, €119 в месяц; обсудить подключение и составить спецификацию можно бесплатно. Kai говорит по-русски и по-английски.</p>

<h2>Частые вопросы</h2>
<div class="faq">
{FAQ}
</div>

<h2>Что дальше</h2>
<p>Если HubSpot нужен уже сейчас — создай service key и подключи по инструкции выше. Если удобнее по кнопке — дождись приложения Kai для HubSpot: оно в разработке.</p>
<div class="cta">
  <a class="btn btn-primary" href="{DOCS}">Инструкция по подключению</a>
  <a class="btn btn-secondary" href="https://app.aii-crm.com/chat?lang=ru">Открыть веб-чат</a>
</div>

<p class="author">Автор: Команда Kai · Обновлено <time datetime="{DATE}">4 ноября 2026</time> · Возможности описаны по состоянию на дату публикации, актуальный статус Kai сообщает в чате.</p>""",
    "en": """<h1>{TITLE}</h1>
<p class="meta">Updated November 4, 2026 · Kai Team · 5 min read</p>

<p class="lead">An AI assistant for HubSpot is a chat where you describe your sales process in plain words and it works with HubSpot through the official API: it shows pipelines and deals, creates deals, contacts, tasks and notes and reviews the funnel. Kai does this in Telegram or in the browser. Today HubSpot connects through the API as a custom CRM; one-click connection is in development.</p>

<section class="tldr" aria-label="TL;DR">
  <h2>TL;DR</h2>
  <ul>
    <li>Today: a HubSpot service key plus Kai's ready-made spec, the custom CRM connection through the API, on the Max plan.</li>
    <li>Works: pipelines and stages, deals (list, search, create, change the stage and amount), contacts, tasks and notes on a deal, funnel analytics.</li>
    <li>In development: a Kai app for HubSpot with a "Sign in with HubSpot" button and an install link, with no keys or JSON.</li>
    <li>Not yet: creating pipelines and fields, companies, automations on HubSpot events.</li>
  </ul>
</section>

<h2>How to connect HubSpot to Kai today</h2>
<ol>
  <li>In HubSpot open <kbd>Development → Keys → Service keys</kbd> and click <kbd>Create service key</kbd>. A super admin or a user with the Developer tools permission can create it.</li>
  <li>Name the key "Kai" and add the scopes <code>crm.objects.deals.read</code>, <code>crm.objects.deals.write</code>, <code>crm.schemas.deals.read</code>, <code>crm.objects.contacts.read</code>, <code>crm.objects.contacts.write</code>. Click <kbd>Create</kbd> and copy the key.</li>
  <li>Open the <a href="{DOCS}">custom CRM connection page</a>, section "Ready-made specs: HubSpot", copy the JSON and paste the key into the <code>token</code> field.</li>
  <li>In the bot <a href="https://t.me/aiicrm_bot">@aiicrm_bot</a> or the <a href="https://app.aii-crm.com/chat?lang=en">web chat</a>: <kbd>/connect</kbd> → "My own CRM via API" → paste the JSON. Kai checks the access and shows your deal pipelines.</li>
</ol>
<div class="note warn">A service key acts on behalf of the HubSpot account, so do not publish it. You can rotate or delete it in HubSpot, and the old key stops working.</div>

<h2>What Kai does in HubSpot</h2>
<ul>
  <li><strong>Pipelines and stages.</strong> Shows deal pipelines and stages and counts deals per stage.</li>
  <li><strong>Deals.</strong> Finds a deal by name, creates a new one in the right pipeline and stage, changes the stage and the amount.</li>
  <li><strong>Contacts.</strong> Creates a contact with a phone and an email.</li>
  <li><strong>Tasks and notes.</strong> Creates a task with a due date and adds a note to a deal.</li>
  <li><strong>Analytics.</strong> How many deals sit at each stage of a pipeline.</li>
</ul>
<p>Every action goes through the official HubSpot API. Everything created stays in your HubSpot account whether or not you keep using the assistant.</p>

<h2>What is in development and what is not there yet</h2>
<div class="table-wrap">
<table>
  <thead><tr><th>Job</th><th>Status in Kai</th><th>What to do now</th></tr></thead>
  <tbody>
    <tr><td>One-click "Sign in with HubSpot"</td><td>In development</td><td>Connect through the API with a service key.</td></tr>
    <tr><td>Creating pipelines, stages and fields from the chat</td><td>Not yet</td><td>Set them up in HubSpot by hand; Kai suggests the structure and writes the spec.</td></tr>
    <tr><td>Companies</td><td>Not yet</td><td>Work with companies in HubSpot.</td></tr>
    <tr><td>Automations on HubSpot events</td><td>Not yet</td><td>HubSpot's built-in workflows, if your HubSpot plan has them.</td></tr>
  </tbody>
</table>
</div>

<h2>With Kai it is one message</h2>
<p>Once connected, you ask Kai the same things you would with any CRM. Examples:</p>
<pre>Show the pipelines and how many deals sit at each stage.</pre>
<pre>Create a deal "Alpha, 20 seats" for 12000 in the Sales Pipeline.</pre>
<pre>Create a task "call back" for the deal "Alpha, 20 seats" for tomorrow and add a note: they asked for an annual invoice.</pre>
<p>Connecting a custom CRM through the API, HubSpot included, is part of the Max plan, €119 per month; discussing the connection and writing the spec are free. Kai speaks English and Russian.</p>

<h2>FAQ</h2>
<div class="faq">
{FAQ}
</div>

<h2>What next</h2>
<p>If you need HubSpot now, create a service key and connect with the steps above. If you would rather connect with one click, wait for the Kai app for HubSpot: it is in development.</p>
<div class="cta">
  <a class="btn btn-primary" href="{DOCS}">Connection guide</a>
  <a class="btn btn-secondary" href="https://app.aii-crm.com/chat?lang=en">Open web chat</a>
</div>

<p class="author">Author: Kai Team · Updated <time datetime="{DATE}">November 4, 2026</time> · Capabilities are described as of the publication date; Kai reports the current status in the chat.</p>""",
}


def page(lang: str, template: str) -> str:
    t = T[lang]
    other = "en" if lang == "ru" else "ru"
    ru_url, en_url = f"https://aii-crm.com/guides/{SLUG}.html", f"https://aii-crm.com/guides/en/{SLUG}.html"
    url = ru_url if lang == "ru" else en_url
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
    body = BODY[lang].replace("{TITLE}", t["title"]).replace("{FAQ}", faq_html).replace("{DOCS}", DOCS[lang]) \
        .replace("{DATE}", DATE)
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
              "prompts": ["ИИ-ассистент для HubSpot", "настройка HubSpot без программиста",
                          "HubSpot AI assistant", "AI for HubSpot setup"]})
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(g, ensure_ascii=False, indent=1))
    print("ok", len(g))


if __name__ == "__main__":
    main()
