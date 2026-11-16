# -*- coding: utf-8 -*-
"""HubSpot и Pipedrive — оба «бета» на сайте (16.11.2026, решение Тихона после полных прогонов).

Факты из кода бота (services/crm/hubspot_provider.supported, pipedrive_provider.supported, handlers/connect):
- HubSpot подключается по кнопке «Войти через HubSpot» или по ссылке установки app.aii-crm.com/install/hubspot (приложение
  Kai, OAuth, без ключей); работают воронки и этапы, поля сделок, сделки, контакты и компании, задачи, заметки, причины
  отказа и источники, аналитика, автоматизации по событиям. Нет: тегов (их нет в HubSpot), приглашения пользователей и
  ролей, виджетов, правила «не ответил N минут».
- Pipedrive: автоматизации по событиям работают с 04.11 (сайт писал «после беты»).
Раньше сайт говорил про HubSpot «в разработке, по service key, тариф Max».

Что делает: гайд HubSpot переписан (RU + EN), гайд Pipedrive поправлен, главная (карточка, FAQ, JSON-LD, описание),
build_en.py, короткие заголовки i18n/seo. Остальные языки — переводчики (i18n_pages.py todo / extract_landing.py).
Запуск один раз: py -3.12 i18n/tools/beta_hubspot_pipedrive.py"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLUG = "hubspot-ai-assistant"
PUBLISHED, UPDATED = "2026-11-04", "2026-11-16"


def rep(s, old, new, cnt=1):
    assert s.count(old) == cnt, (s.count(old), old[:90])
    return s.replace(old, new)


def jq(s: str) -> str:
    """Текст так, как он лежит внутри JSON-LD (кавычки экранированы)."""
    return json.dumps(s, ensure_ascii=False)[1:-1]


# ═════════════════════════ гайд HubSpot ═════════════════════════
_spec = importlib.util.spec_from_file_location("add_hubspot_guide", os.path.join(HERE, "i18n", "tools", "add_hubspot_guide.py"))
hs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hs)

hs.T["ru"].update({
    "desc": ("Как подключить HubSpot к ИИ-ассистенту Kai по кнопке, без ключей, и что он делает в HubSpot: воронки, поля, "
             "сделки, контакты, компании, задачи, автоматизации. Поддержка в бете."),
    "og": ("Kai работает с HubSpot: воронки, поля, сделки, контакты, компании, задачи и автоматизации по сообщению в "
           "Telegram или в браузере. Подключение по кнопке, поддержка в бете."),
})
hs.T["en"].update({
    "desc": ("How to connect HubSpot to the Kai AI assistant with one click, no keys, and what it does in HubSpot: pipelines, "
             "properties, deals, contacts, companies, tasks, automations. Support is in beta."),
    "og": ("Kai works with HubSpot: pipelines, properties, deals, contacts, companies, tasks and automations from a message in "
           "Telegram or the browser. One-click connection, support is in beta."),
})

hs.FAQ["ru"] = [
    ("Есть ли ИИ-ассистент, который настраивает HubSpot по сообщению?",
     "Да, Kai. Ты описываешь процесс продаж обычными словами в Telegram или в браузере, а Kai создаёт в HubSpot воронки и "
     "этапы, поля, сделки, контакты, компании, задачи и заметки через официальный API, разбирает воронку и запускает правила "
     "по событиям. Поддержка HubSpot — в бете."),
    ("Как подключить HubSpot к Kai?",
     "Открой ссылку установки app.aii-crm.com/install/hubspot, разреши доступ в HubSpot и на странице «Kai установлен» нажми "
     "«Открыть Kai в Telegram» или «Продолжить в браузере». Второй способ — в боте: /connect → HubSpot (бета) → «Войти через "
     "HubSpot». Ключи и JSON не нужны."),
    ("Kai умеет автоматизации в HubSpot?",
     "Да, с тарифа Pro. Правило на событие HubSpot — сделка создана или перешла на этап — ставит задачу или присылает "
     "уведомление. Правило описываешь словами, Kai показывает его перед включением."),
    ("С какого тарифа доступен HubSpot?",
     "С тарифа Start, €29 в месяц за одну CRM; автоматизации по событиям — с Pro, €59. Первые 3 дня — триал без карты, этого "
     "хватает, чтобы проверить Kai на своём аккаунте HubSpot."),
]
hs.FAQ["en"] = [
    ("Is there an AI assistant that sets up HubSpot from a chat message?",
     "Yes, Kai. You describe your sales process in plain words in Telegram or the browser, and Kai creates pipelines and "
     "stages, properties, deals, contacts, companies, tasks and notes in HubSpot through the official API, reviews the funnel "
     "and runs rules on events. HubSpot support is in beta."),
    ("How do I connect HubSpot to Kai?",
     "Open the install link app.aii-crm.com/install/hubspot, allow access in HubSpot and on the \"Kai is installed\" page "
     "press \"Open Kai in Telegram\" or \"Continue in the browser\". One more way in the bot: /connect → HubSpot (beta) → "
     "\"Sign in with HubSpot\". No keys, no JSON."),
    ("Can Kai build automations in HubSpot?",
     "Yes, from the Pro plan. A rule on a HubSpot event (a deal is created or moves to a stage) creates a task or sends a "
     "notification. You describe the rule in words, and Kai shows it before switching it on."),
    ("Which plan do I need for HubSpot?",
     "Any plan from Start, €29 per month for one CRM; event automations start on Pro, €59. The first 3 days are a trial "
     "without a card, enough to test Kai on your own HubSpot account."),
]

hs.BODY["ru"] = """<h1>{TITLE}</h1>
<p class="meta">Обновлено 16 ноября 2026 · Команда Kai · 5 минут чтения</p>

<p class="lead">ИИ-ассистент для HubSpot — это чат, в котором ты описываешь процесс продаж обычными словами, а он собирает его в HubSpot через официальный API: воронки и этапы, поля, сделки, контакты, компании, задачи и заметки. Kai делает это в Telegram или в браузере. Поддержка HubSpot в бете: подключение по кнопке, структура, данные, аналитика и автоматизации по событиям уже работают.</p>

<section class="tldr" aria-label="Коротко">
  <h2>Коротко</h2>
  <ul>
    <li>Установка — по ссылке <a href="https://app.aii-crm.com/install/hubspot">app.aii-crm.com/install/hubspot</a>: HubSpot спросит разрешение, потом Kai привяжет аккаунт HubSpot к твоему аккаунту в Telegram или в веб-чате. Ключи и JSON не нужны.</li>
    <li>Работает: воронки и этапы, поля сделок со списками вариантов, сделки, контакты, компании, задачи, заметки, причины отказа и источники, аналитика воронки, автоматизации по событиям.</li>
    <li>Пока нет: тегов (их нет в самом HubSpot), приглашения пользователей и ролей, кнопок или панелей внутри HubSpot.</li>
    <li>Доступно с тарифа Start, €29 в месяц; автоматизации — с тарифа Pro. Первые 3 дня — триал.</li>
  </ul>
</section>

<h2>Как подключить HubSpot к Kai</h2>
<ol>
  <li>Открой <a href="https://app.aii-crm.com/install/hubspot">ссылку установки</a> и войди в HubSpot, если он попросит.</li>
  <li>Выбери аккаунт HubSpot и посмотри, к каким данным Kai просит доступ. Галочки доступа к компаниям и полям лучше оставить: без них Kai не сможет вести компании и поля. Разреши доступ.</li>
  <li>На странице «Kai установлен в HubSpot» нажми «Открыть Kai в Telegram» или «Продолжить в браузере». Ссылка срабатывает один раз и живёт 30 минут: она привязывает этот аккаунт HubSpot к твоему аккаунту Kai.</li>
  <li>Kai подтвердит подключение и спросит, что настраиваем.</li>
</ol>
<p>Второй способ — прямо в боте <a href="https://t.me/aiicrm_bot">@aiicrm_bot</a> или в <a href="https://app.aii-crm.com/chat?lang=ru">веб-чате</a>: команда <kbd>/connect</kbd> → «HubSpot (бета)» → «Войти через HubSpot».</p>
<div class="note warn">Вход через HubSpot идёт по OAuth: пароль от HubSpot Kai не видит. Отключить Kai можно в HubSpot, в списке подключённых приложений, — доступ пропадёт сразу.</div>

<h2>Что Kai настраивает в HubSpot</h2>
<ul>
  <li><strong>Воронки и этапы.</strong> Новая воронка с этапами одним сообщением; добавить, переименовать или удалить этап. Сколько воронок можно создать, решает твой тариф HubSpot.</li>
  <li><strong>Поля.</strong> Свои поля сделок, включая списки вариантов, и их значения в сделке.</li>
  <li><strong>Сделки.</strong> Создать в нужной воронке и на нужном этапе, передвинуть по этапам, поменять сумму, найти; ссылка на карточку сделки в HubSpot.</li>
  <li><strong>Контакты и компании.</strong> Создать и привязать к сделке.</li>
  <li><strong>Задачи и заметки.</strong> Задача со сроком по сделке и заметка прямо из чата.</li>
  <li><strong>Аналитика воронки.</strong> Сколько сделок на каждом этапе, причины отказа, «здоровье» конкретной сделки.</li>
  <li><strong>Автоматизации по событиям.</strong> Сделка создана или перешла на этап — Kai ставит задачу или присылает уведомление.</li>
</ul>
<p>Все действия идут через официальный API HubSpot. Всё созданное остаётся в твоём аккаунте HubSpot, даже если ты перестанешь пользоваться ассистентом.</p>

<h2>Чего Kai в HubSpot пока не делает</h2>
<div class="table-wrap">
<table>
  <thead><tr><th>Задача</th><th>Статус в Kai</th><th>Что делать сейчас</th></tr></thead>
  <tbody>
    <tr><td>Теги на сделках и контактах</td><td>Нет в HubSpot</td><td>Поле-список в сделке: Kai создаст его вместе с вариантами.</td></tr>
    <tr><td>Пригласить пользователя, настроить роли</td><td>Пока нет</td><td>Настройки HubSpot → «Пользователи и команды».</td></tr>
    <tr><td>Правило «клиент не ответил N минут»</td><td>Пока нет</td><td>Правило на новую сделку или смену этапа.</td></tr>
    <tr><td>Кнопки и панели Kai внутри HubSpot</td><td>Пока нет</td><td>Работай с Kai в чате: в Telegram или в браузере.</td></tr>
  </tbody>
</table>
</div>
<p>Честный итог: сегодня Kai для HubSpot — это настройка структуры, порядок в данных, задачи, разбор воронки и правила по событиям. Поддержка в бете: если что-то сработало не так, напиши в поддержку прямо в чате.</p>

<h2>С Kai это одно сообщение</h2>
<p>Ты описываешь бизнес, Kai задаёт уточняющие вопросы, показывает план, после подтверждения создаёт всё через API и присылает отчёт. Примеры:</p>
<pre>Создай в HubSpot воронку для B2B-продаж: Новый лид → Квалификация → Демо → КП → Договор. Добавь в сделки числовое поле «Бюджет».</pre>
<pre>Создай сделку «Альфа, 20 мест» на 12000 в воронке Sales Pipeline, добавь контакт Анна Смирнова и компанию «Альфа».</pre>
<pre>Когда сделка переходит на этап «Договор», ставь задачу «выставить счёт» на завтра.</pre>
<p>Тарифы те же, что для других CRM: Start €29 в месяц за одну CRM, Pro €59 до трёх CRM, Max €119 до десяти. Первые 3 дня — триал без карты, около 25 запросов на функциях Start. Kai говорит по-русски и по-английски.</p>

<h2>Частые вопросы</h2>
<div class="faq">
{FAQ}
</div>

<h2>Что дальше</h2>
<p>Открой ссылку установки, разреши доступ и попроси Kai показать воронки — так за минуту видно, что ассистент работает с твоим аккаунтом.</p>
<div class="cta">
  <a class="btn btn-primary" href="https://app.aii-crm.com/install/hubspot">Установить Kai в HubSpot</a>
  <a class="btn btn-secondary" href="https://app.aii-crm.com/chat?lang=ru">Открыть веб-чат</a>
</div>

<p class="author">Автор: Команда Kai · Обновлено <time datetime="2026-11-16">16 ноября 2026</time> · Возможности и ограничения описаны на дату публикации; актуальный статус Kai сообщает в чате.</p>"""

hs.BODY["en"] = """<h1>{TITLE}</h1>
<p class="meta">Updated November 16, 2026 · Kai Team · 5 min read</p>

<p class="lead">An AI assistant for HubSpot is a chat where you describe your sales process in plain words and it builds it in HubSpot through the official API: pipelines and stages, properties, deals, contacts, companies, tasks and notes. Kai does this in Telegram or in the browser. HubSpot support is in beta: one-click connection, structure, data, analytics and event automations already work.</p>

<section class="tldr" aria-label="TL;DR">
  <h2>TL;DR</h2>
  <ul>
    <li>Install from the link <a href="https://app.aii-crm.com/install/hubspot">app.aii-crm.com/install/hubspot</a>: HubSpot asks for permission, then Kai links the HubSpot account to your account in Telegram or the web chat. No keys, no JSON.</li>
    <li>Works: pipelines and stages, deal properties with option lists, deals, contacts, companies, tasks, notes, loss reasons and lead sources, funnel analytics, event automations.</li>
    <li>Not yet: tags (HubSpot itself has none), inviting users and roles, buttons or panels inside HubSpot.</li>
    <li>Available from the Start plan, €29 per month; automations start on the Pro plan. The first 3 days are a trial.</li>
  </ul>
</section>

<h2>How to connect HubSpot to Kai</h2>
<ol>
  <li>Open the <a href="https://app.aii-crm.com/install/hubspot">install link</a> and sign in to HubSpot if it asks.</li>
  <li>Pick the HubSpot account and check which data Kai asks to access. Keep the permissions for companies and properties ticked: without them Kai can't manage companies and properties. Allow the access.</li>
  <li>On the "Kai is installed in HubSpot" page press "Open Kai in Telegram" or "Continue in the browser". The link works once, for 30 minutes: it ties this HubSpot account to your Kai account.</li>
  <li>Kai confirms the connection and asks what to set up.</li>
</ol>
<p>One more way, right in the bot <a href="https://t.me/aiicrm_bot">@aiicrm_bot</a> or the <a href="https://app.aii-crm.com/chat?lang=en">web chat</a>: the <kbd>/connect</kbd> command → "HubSpot (beta)" → "Sign in with HubSpot".</p>
<div class="note warn">Signing in with HubSpot uses OAuth: Kai never sees your HubSpot password. You can disconnect Kai in HubSpot, in the list of connected apps, and the access is gone at once.</div>

<h2>What Kai sets up in HubSpot</h2>
<ul>
  <li><strong>Pipelines and stages.</strong> A new pipeline with stages from one message; add, rename or delete a stage. How many pipelines you can have is set by your HubSpot plan.</li>
  <li><strong>Properties.</strong> Custom deal properties, including option lists, and their values on a deal.</li>
  <li><strong>Deals.</strong> Create in the right pipeline and stage, move between stages, change the amount, search; a link to the deal record in HubSpot.</li>
  <li><strong>Contacts and companies.</strong> Create them and link them to a deal.</li>
  <li><strong>Tasks and notes.</strong> A task with a due date on a deal and a note, straight from the chat.</li>
  <li><strong>Funnel analytics.</strong> Deals per stage, loss reasons, the "health" of a specific deal.</li>
  <li><strong>Event automations.</strong> A deal is created or moves to a stage, and Kai creates a task or sends a notification.</li>
</ul>
<p>Every action goes through the official HubSpot API. Everything created stays in your HubSpot account whether or not you keep using the assistant.</p>

<h2>What Kai does not do in HubSpot yet</h2>
<div class="table-wrap">
<table>
  <thead><tr><th>Job</th><th>Status in Kai</th><th>What to do now</th></tr></thead>
  <tbody>
    <tr><td>Tags on deals and contacts</td><td>Not in HubSpot</td><td>A list property on the deal: Kai creates it together with the options.</td></tr>
    <tr><td>Inviting a user, setting up roles</td><td>Not yet</td><td>HubSpot settings → Users &amp; Teams.</td></tr>
    <tr><td>A rule "the client has not replied for N minutes"</td><td>Not yet</td><td>A rule on a new deal or a stage change.</td></tr>
    <tr><td>Kai buttons and panels inside HubSpot</td><td>Not yet</td><td>Work with Kai in the chat: in Telegram or in the browser.</td></tr>
  </tbody>
</table>
</div>
<p>The honest summary: today Kai for HubSpot sets up the structure, keeps the data in order, handles tasks, reviews the funnel and runs rules on events. Support is in beta: if something goes wrong, write to support right in the chat.</p>

<h2>With Kai it is one message</h2>
<p>You describe the business, Kai asks clarifying questions, shows a plan, creates everything through the API once you confirm and sends a report. Examples:</p>
<pre>Create a HubSpot pipeline for B2B sales: New lead → Qualified → Demo → Proposal → Contract. Add a number property Budget to deals.</pre>
<pre>Create a deal "Alpha, 20 seats" for 12000 in the Sales Pipeline, add the contact Anna Smith and the company Alpha.</pre>
<pre>When a deal moves to the Contract stage, create a task "send the invoice" for tomorrow.</pre>
<p>Plans are the same as for the other CRMs: Start €29 per month for one CRM, Pro €59 for up to three CRMs, Max €119 for up to ten. The first 3 days are a trial, no card, about 25 requests on Start features. Kai speaks English and Russian.</p>

<h2>FAQ</h2>
<div class="faq">
{FAQ}
</div>

<h2>What next</h2>
<p>Open the install link, allow access and ask Kai to show your pipelines: in a minute you see the assistant working with your account.</p>
<div class="cta">
  <a class="btn btn-primary" href="https://app.aii-crm.com/install/hubspot">Install Kai in HubSpot</a>
  <a class="btn btn-secondary" href="https://app.aii-crm.com/chat?lang=en">Open web chat</a>
</div>

<p class="author">Author: Kai Team · Updated <time datetime="2026-11-16">November 16, 2026</time> · Capabilities and limits are described as of the publication date; Kai reports the current status in the chat.</p>"""


def hubspot_page(lang: str, template: str) -> str:
    h = hs.page(lang, template)                      # дата публикации прежняя, дата правки — сегодняшняя
    h = rep(h, f'<meta property="article:modified_time" content="{PUBLISHED}">',
            f'<meta property="article:modified_time" content="{UPDATED}">')
    h = rep(h, f'"dateModified": "{PUBLISHED}"', f'"dateModified": "{UPDATED}"')
    return h


# ═════════════════════════ гайд Pipedrive: точечные правки ═════════════════════════
PD = {
    "ru": [
        ("Обновлено 3 ноября 2026 · Команда Kai", "Обновлено 16 ноября 2026 · Команда Kai"),
        ('Обновлено <time datetime="2026-11-03">3 ноября 2026</time>', 'Обновлено <time datetime="2026-11-16">16 ноября 2026</time>'),
        ("Поддержка Pipedrive в бете: структура, данные, задачи и аналитика работают, автоматизации на событиях Pipedrive — следующим шагом.",
         "Поддержка Pipedrive в бете: структура, данные, задачи, аналитика и автоматизации по событиям уже работают."),
        ("задачи, заметки, пользователи, аналитика воронки с выигранными и проигранными.</li>",
         "задачи, заметки, метки, пользователи, аналитика воронки с выигранными и проигранными, автоматизации по событиям.</li>"),
        ("<li>Пока нет: правил на событиях Pipedrive (автоматизаций и интеграций Kai) и кнопок или панелей внутри Pipedrive.</li>",
         "<li>Пока нет: кнопок и панелей Kai внутри Pipedrive и правила «клиент не ответил N минут».</li>"),
        ("<li>Доступно с тарифа Start, €29 в месяц. Первые 3 дня — триал.</li>",
         "<li>Доступно с тарифа Start, €29 в месяц; автоматизации — с тарифа Pro. Первые 3 дня — триал.</li>"),
        ('  <li><strong>Аналитика воронки.</strong> Сколько сделок на каждом этапе, сколько выиграно и проиграно, «здоровье» конкретной сделки.</li>\n',
         '  <li><strong>Аналитика воронки.</strong> Сколько сделок на каждом этапе, сколько выиграно и проиграно, «здоровье» конкретной сделки.</li>\n'
         '  <li><strong>Автоматизации по событиям.</strong> Сделка создана или перешла на этап — Kai ставит задачу или присылает уведомление.</li>\n'),
        ("    <tr><td>Правила на событиях: сделка перешла на этап → задача, уведомление</td><td>После беты</td><td>Встроенные автоматизации Pipedrive, если они есть в твоём тарифе Pipedrive.</td></tr>\n"
         "    <tr><td>Интеграции с другими сервисами по событиям</td><td>После беты</td><td>Приложения из маркетплейса Pipedrive или разработчик.</td></tr>\n",
         "    <tr><td>Правило «клиент не ответил N минут»</td><td>Пока нет</td><td>Правило на новую сделку или смену этапа.</td></tr>\n"
         "    <tr><td>Обязательное поле на этапе</td><td>Нет в API Pipedrive</td><td>Настройки Pipedrive → «Поля данных» → поле → «Важное» или «Обязательное».</td></tr>\n"),
        ("<p>Честный итог: сегодня Kai для Pipedrive — это настройка структуры, порядок в данных, задачи и разбор воронки. Автоматизации по событиям уже работают для amoCRM и Kommo и придут в Pipedrive после беты.</p>",
         "<p>Честный итог: сегодня Kai для Pipedrive — это настройка структуры, порядок в данных, задачи, разбор воронки и правила по событиям. Поддержка в бете: если что-то сработало не так, напиши в поддержку прямо в чате.</p>"),
    ],
    "en": [
        ("Updated November 3, 2026 · Kai Team", "Updated November 16, 2026 · Kai Team"),
        ('Updated <time datetime="2026-11-03">November 3, 2026</time>', 'Updated <time datetime="2026-11-16">November 16, 2026</time>'),
        ("Pipedrive support is in beta: structure, data, activities and analytics work; automations on Pipedrive events come next.",
         "Pipedrive support is in beta: structure, data, activities, analytics and event automations already work."),
        ("activities, notes, users, funnel analytics with won and lost deals.</li>",
         "activities, notes, labels, users, funnel analytics with won and lost deals, event automations.</li>"),
        ("<li>Not yet: rules on Pipedrive events (Kai's automations and integrations) and buttons or panels inside Pipedrive.</li>",
         "<li>Not yet: Kai buttons and panels inside Pipedrive and the rule \"the client has not replied for N minutes\".</li>"),
        ("<li>Available from the Start plan, €29 per month. The first 3 days are a trial.</li>",
         "<li>Available from the Start plan, €29 per month; automations start on the Pro plan. The first 3 days are a trial.</li>"),
        ('  <li><strong>Funnel analytics.</strong> Deals per stage, won and lost deals, the "health" of a specific deal.</li>\n',
         '  <li><strong>Funnel analytics.</strong> Deals per stage, won and lost deals, the "health" of a specific deal.</li>\n'
         '  <li><strong>Event automations.</strong> A deal is created or moves to a stage, and Kai creates an activity or sends a notification.</li>\n'),
        ("    <tr><td>Rules on events: a deal moves to a stage → an activity, a notification</td><td>After the beta</td><td>Pipedrive's built-in automations, if your Pipedrive plan has them.</td></tr>\n"
         "    <tr><td>Event-driven integrations with other services</td><td>After the beta</td><td>Apps from the Pipedrive Marketplace or a developer.</td></tr>\n",
         "    <tr><td>A rule \"the client has not replied for N minutes\"</td><td>Not yet</td><td>A rule on a new deal or a stage change.</td></tr>\n"
         "    <tr><td>A required field at a stage</td><td>Not in the Pipedrive API</td><td>Pipedrive settings → Data fields → the field → Important or Required.</td></tr>\n"),
        ("<p>The honest summary: today Kai for Pipedrive sets up the structure, keeps the data in order, handles activities and reviews the funnel. Event automations already work for amoCRM and Kommo and come to Pipedrive after the beta.</p>",
         "<p>The honest summary: today Kai for Pipedrive sets up the structure, keeps the data in order, handles activities, reviews the funnel and runs rules on events. Support is in beta: if something goes wrong, write to support right in the chat.</p>"),
    ],
}
# ответы FAQ гайда Pipedrive: в странице они лежат дважды — в разметке и в JSON-LD
PD_FAQ = {
    "ru": [
        ("Да, Kai. Ты описываешь процесс продаж обычными словами в Telegram или в браузере, а Kai создаёт в Pipedrive воронки и этапы, поля, сделки, контакты, организации, задачи и заметки через официальный API и разбирает воронку. Поддержка Pipedrive — в бете.",
         "Да, Kai. Ты описываешь процесс продаж обычными словами в Telegram или в браузере, а Kai создаёт в Pipedrive воронки и этапы, поля, сделки, контакты, организации, задачи и заметки через официальный API, разбирает воронку и запускает правила по событиям. Поддержка Pipedrive — в бете."),
        ("Пока нет. Правила на событиях Pipedrive (сделка перешла на этап → задача или уведомление) и интеграции по событиям появятся после беты. Сейчас Kai настраивает структуру, ведёт данные и задачи и разбирает воронку.",
         "Да, с тарифа Pro. Правило на событие Pipedrive — сделка создана или перешла на этап — ставит задачу или присылает уведомление. Правило описываешь словами, Kai показывает его перед включением."),
        ("С тарифа Start, €29 в месяц за одну CRM. Первые 3 дня — триал без карты, этого хватает, чтобы проверить Kai на своей компании в Pipedrive.",
         "С тарифа Start, €29 в месяц за одну CRM; автоматизации по событиям — с Pro, €59. Первые 3 дня — триал без карты, этого хватает, чтобы проверить Kai на своей компании в Pipedrive."),
    ],
    "en": [
        ("Yes, Kai. You describe your sales process in plain words in Telegram or the browser, and Kai creates pipelines and stages, fields, deals, people, organizations, activities and notes in Pipedrive through the official API and reviews the funnel. Pipedrive support is in beta.",
         "Yes, Kai. You describe your sales process in plain words in Telegram or the browser, and Kai creates pipelines and stages, fields, deals, people, organizations, activities and notes in Pipedrive through the official API, reviews the funnel and runs rules on events. Pipedrive support is in beta."),
        ("Not yet. Rules on Pipedrive events (a deal moves to a stage → a task or a notification) and event-driven integrations come after the beta. Today Kai sets up the structure, manages data and activities and reviews the funnel.",
         "Yes, from the Pro plan. A rule on a Pipedrive event (a deal is created or moves to a stage) creates an activity or sends a notification. You describe the rule in words, and Kai shows it before switching it on."),
        ("Any plan from Start, €29 per month for one CRM. The first 3 days are a trial without a card, enough to test Kai on your own Pipedrive company.",
         "Any plan from Start, €29 per month for one CRM; event automations start on Pro, €59. The first 3 days are a trial without a card, enough to test Kai on your own Pipedrive company."),
    ],
}
PD_META = {     # описание гайда Pipedrive: «чего пока нет» осталось, «автоматизаций нет» — уже неправда
    "ru": ("desc_ru", None),
    "en": ("desc_en", None),
}


def patch_pipedrive(h: str, lang: str) -> str:
    for old, new in PD[lang]:
        h = rep(h, old, new)
    for old, new in PD_FAQ[lang]:
        h = rep(h, f"<p>{old}</p>", f"<p>{new}</p>")
        h = rep(h, jq(old), jq(new))
    h = h.replace('<meta property="article:modified_time" content="2026-11-03">',
                  f'<meta property="article:modified_time" content="{UPDATED}">')
    h = h.replace('"dateModified": "2026-11-03"', f'"dateModified": "{UPDATED}"')
    return h


def guides():
    p = os.path.join(HERE, "guides.json")
    g = json.load(io.open(p, encoding="utf-8"))
    b = next(x for x in g if x["slug"] == "bitrix24-ai-assistant")
    x = next(x for x in g if x["slug"] == SLUG)
    x.update({"desc_ru": hs.T["ru"]["desc"], "desc_en": hs.T["en"]["desc"],
              "html_ru": hubspot_page("ru", b["html_ru"]), "html_en": hubspot_page("en", b["html_en"])})
    pd = next(x for x in g if x["slug"] == "pipedrive-ai-assistant")
    pd["html_ru"], pd["html_en"] = patch_pipedrive(pd["html_ru"], "ru"), patch_pipedrive(pd["html_en"], "en")
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(g, ensure_ascii=False, indent=1))
    print("guides.json ok")


# ═════════════════════════ главная ═════════════════════════
HOME = {
    "tip_ru": "HubSpot: установить Kai в свой HubSpot в один клик",
    "tip_en": "HubSpot: install Kai into your HubSpot in one click",
    "feat_ru": "Подключение HubSpot (бета): воронки, сделки, компании, задачи, аналитика",
    "feat_en": "HubSpot connection (beta): pipelines, deals, companies, tasks, analytics",
    "pd_old_ru": ("Да, в бете и с тарифа Start. Подключение — ссылкой установки из Pipedrive, кнопкой «Войти через Pipedrive» в боте или личным API-токеном. Kai настраивает воронки, этапы и поля, ведёт сделки, контакты, организации, задачи и заметки и разбирает воронку. Автоматизаций по событиям для Pipedrive пока нет — они появятся после беты."),
    "pd_new_ru": ("Да, в бете и с тарифа Start. Подключение — ссылкой установки из Pipedrive, кнопкой «Войти через Pipedrive» в боте или личным API-токеном. Kai настраивает воронки, этапы и поля, ведёт сделки, контакты, организации, задачи и заметки и разбирает воронку. Автоматизации по событиям Pipedrive работают с тарифа Pro."),
    "pd_old_en": ("Yes, in beta, from the Start plan. Connect with the install link from Pipedrive, the “Sign in with Pipedrive” button in the bot or a personal API token. Kai sets up pipelines, stages and fields, manages deals, people, organizations, activities and notes and reviews the funnel. Event automations for Pipedrive are not there yet — they come after the beta."),
    "pd_new_en": ("Yes, in beta, from the Start plan. Connect with the install link from Pipedrive, the “Sign in with Pipedrive” button in the bot or a personal API token. Kai sets up pipelines, stages and fields, manages deals, people, organizations, activities and notes and reviews the funnel. Automations on Pipedrive events work from the Pro plan."),
    "hs_old_ru": ("Подключение по кнопке — в разработке. Уже сейчас HubSpot подключается по API как своя CRM: ключ service key в HubSpot и готовая спецификация Kai, на тарифе Max. Kai видит воронки и сделки, создаёт сделки, контакты, задачи и заметки."),
    "hs_new_ru": ("Да, в бете и с тарифа Start. Подключение — кнопкой «Войти через HubSpot» в боте или ссылкой установки, без ключей и JSON. Kai настраивает воронки, этапы и поля, ведёт сделки, контакты, компании, задачи и заметки и разбирает воронку. Автоматизации по событиям HubSpot работают с тарифа Pro."),
    "hs_old_en": ("One-click connection is in development. Today HubSpot connects through the API as a custom CRM: a HubSpot service key plus Kai’s ready-made spec, on the Max plan. Kai sees pipelines and deals and creates deals, contacts, tasks and notes."),
    "hs_new_en": ("Yes, in beta, from the Start plan. Connect with the “Sign in with HubSpot” button in the bot or the install link, with no keys or JSON. Kai sets up pipelines, stages and properties, manages deals, contacts, companies, tasks and notes and reviews the funnel. Automations on HubSpot events work from the Pro plan."),
}


def home():
    p = os.path.join(HERE, "index.html")
    s = io.open(p, encoding="utf-8").read()
    # карточка: «в разработке» → «бета», ведёт на установку (как Pipedrive)
    s = rep(s, '''      <a href="guides/hubspot-ai-assistant.html" class="int-logo soon hs-link"
         title="HubSpot: подключение по API уже сейчас, по кнопке — в разработке"
         data-ru-title="HubSpot: подключение по API уже сейчас, по кнопке — в разработке"
         data-en-title="HubSpot: connect via API today, one-click connection in development"
         data-ru-href="guides/hubspot-ai-assistant.html" data-en-href="guides/en/hubspot-ai-assistant.html">''',
            f'''      <a href="https://app.aii-crm.com/install/hubspot" target="_blank" rel="noopener" class="int-logo soon hs-link"
         title="{HOME['tip_ru']}"
         data-ru-title="{HOME['tip_ru']}"
         data-en-title="{HOME['tip_en']}">''')
    s = rep(s, '<span class="soon-badge" data-ru="в разработке" data-en="in development">в разработке</span>',
            '<span class="soon-badge" data-ru="бета" data-en="beta">бета</span>')
    # видимый FAQ (в разметке текст стоит трижды: data-ru, data-en и содержимое) и JSON-LD
    for key in ("pd", "hs"):
        s = rep(s, HOME[f"{key}_old_ru"], HOME[f"{key}_new_ru"], 3)
        s = rep(s, HOME[f"{key}_old_en"], HOME[f"{key}_new_en"], 1)
    s = rep(s, '"HubSpot по API (подключение по кнопке — в разработке)"', json.dumps(HOME["feat_ru"], ensure_ascii=False))
    # описания: HubSpot в перечне CRM
    s = rep(s, "amoCRM, Kommo, Bitrix24, Pipedrive или свою CRM по API. Воронки, поля, задачи, автоматизации. 3 дня триала.",
            "amoCRM, Kommo, Bitrix24, Pipedrive, HubSpot или свою CRM по API. Воронки, поля, задачи, автоматизации. 3 дня триала.")
    s = rep(s, "в Telegram или в браузере: amoCRM, Kommo, Bitrix24, Pipedrive или своя самописная CRM по API.",
            "в Telegram или в браузере: amoCRM, Kommo, Bitrix24, Pipedrive, HubSpot или своя самописная CRM по API.")
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)

    p = os.path.join(HERE, "build_en.py")
    s = io.open(p, encoding="utf-8").read()
    s = rep(s, '"HubSpot via API (one-click connection in development)"', json.dumps(HOME["feat_en"]))
    s = rep(s, json.dumps(HOME["pd_old_en"], ensure_ascii=False), json.dumps(HOME["pd_new_en"], ensure_ascii=False))
    s = rep(s, json.dumps(HOME["hs_old_en"], ensure_ascii=False), json.dumps(HOME["hs_new_en"], ensure_ascii=False))
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("index.html, build_en.py ok")


# ═════════════════════════ короткие заголовки для выдачи ═════════════════════════
SEO = {
    "ru": {"guides/hubspot-ai-assistant.html":
           ("ИИ-ассистент для HubSpot: настройка CRM по сообщению в чате | Kai",
            "Kai настраивает HubSpot по сообщению в чате: воронки, поля, сделки, компании, задачи, автоматизации. "
            "Подключение по кнопке, что работает в бете и чего пока нет."),
           "guides/pipedrive-ai-assistant.html":
           ("ИИ-ассистент для Pipedrive: настройка CRM по сообщению в чате | Kai",
            "Kai настраивает Pipedrive по сообщению в чате: воронки, поля, сделки, задачи, автоматизации. Установка по "
            "ссылке, что работает в бете и чего пока нет.")},
    "en": {"guides/en/hubspot-ai-assistant.html":
           ("HubSpot AI assistant: set up your CRM from a chat message | Kai",
            "Kai sets up HubSpot from a chat message: pipelines, properties, deals, tasks, automations. One-click "
            "connection, what works in the beta, what does not yet."),
           "guides/en/pipedrive-ai-assistant.html":
           ("Pipedrive AI assistant: set up your CRM from a chat message | Kai",
            "Kai sets up Pipedrive from a chat message: pipelines, fields, deals, activities, automations. Install link, "
            "what works in the beta, what does not yet.")},
}


def seo():
    for lang, items in SEO.items():
        fp = os.path.join(HERE, "i18n", "seo", f"{lang}.json")
        d = json.load(io.open(fp, encoding="utf-8"))
        for path, (title, desc) in items.items():
            assert len(title) <= 70 and 70 <= len(desc) <= 160, (lang, path, len(title), len(desc))
            assert path in d, path
            d[path] = {"title": title, "description": desc}
        if lang == "ru":            # главная: HubSpot в перечне CRM
            home_ru = d[""]
            new = home_ru["description"].replace("Bitrix24, Pipedrive или свою CRM", "Bitrix24, Pipedrive, HubSpot или свою CRM")
            assert new != home_ru["description"] and len(new) <= 160, len(new)
            home_ru["description"] = new
        io.open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
    print("i18n/seo ok")


if __name__ == "__main__":
    guides()
    home()
    seo()
