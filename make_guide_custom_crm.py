# -*- coding: utf-8 -*-
"""Гайд «Как подключить ИИ-агента к самописной CRM» (01.11.2026, Тихон: «про кастомные CRM ни слова — добавить и прописать
везде, плюс ключевые слова для SEO и AI-поиска»). Собирает html_ru/html_en и кладёт запись в guides.json после гайда про
Bitrix24; шапка, CSS и hw-скрипт берутся из существующего гайда, чтобы страницы не разъехались. Факты — из кода бота
(services/custom_crm.py, custom_crm_docs.py, billing.py): способы авторизации, обязательная операция, лимиты, тариф.
Запуск: py -3.12 make_guide_custom_crm.py && py -3.12 build_guides.py"""
import html
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://aii-crm.com/"
SLUG = "ai-agent-for-custom-crm"
DATE = "2026-11-01"
DOCS = "https://app.aii-crm.com/docs/custom-crm?lang="
GUIDES = os.path.join(HERE, "guides.json")

RAW = io.open(GUIDES, encoding="utf-8").read()
guides = json.loads(RAW)
_tpl = next(g for g in guides if g["slug"] == "bitrix24-ai-assistant")["html_ru"]
CSS = re.search(r"<style>.*?</style>", _tpl, re.S).group(0)
HW = re.search(r"<script>\(function\(\)\{try\{var p=.*?</script>", _tpl, re.S).group(0)

RU = dict(
    lang="ru",
    h1="Как подключить ИИ-агента к самописной CRM: по API, без переписывания системы",
    title_tag="ИИ-агент для самописной CRM: как подключить по API без переписывания системы | Kai",
    og_title="Как подключить ИИ-агента к самописной CRM по API",
    desc=("Что нужно, чтобы ИИ-агент работал с вашей собственной (самописной, кастомной) CRM: REST API с JSON, авторизация "
          "OAuth 2.0 / API-ключ / bearer, спецификация коннектора. Три способа подключить, что агент умеет после, границы и "
          "безопасность — на примере Kai."),
    og_desc=("Своя CRM с REST API подключается к ИИ-агенту без переписывания: адрес API, авторизация, список воронок — и дальше "
             "воронки, сделки, задачи и автоматизации словами в чате. Что нужно, как подключить, где границы."),
    keywords=("подключить ИИ-агента к самописной CRM, ИИ для кастомной CRM, ИИ-ассистент для собственной CRM по API, интеграция "
              "искусственного интеллекта с CRM по REST API, своя CRM ИИ-агент, AI-агент для custom CRM"),
    author_meta="Команда Kai",
    meta="Обновлено 1 ноября 2026 · Команда Kai · 8 минут чтения",
    crumb="ИИ-агент для самописной CRM",
    crumbs_label="Хлебные крошки",
    nav=("Сайт", "Telegram-бот", "EN"),
    guides_label="Гайды",
    lead=("У многих компаний CRM своя: написана под процесс, живёт на своём сервере, и ни один готовый «ИИ-ассистент для amoCRM» "
          "к ней не подходит. Переписывать систему ради этого не нужно. Если у CRM есть REST API, который отвечает JSON, ИИ-агент "
          "подключается к ней так же, как к коробочной: ты описываешь, где API живёт, как авторизоваться и какой запрос за что "
          "отвечает, а дальше настраиваешь воронки, ставишь задачи и заводишь автоматизации словами в чате. Этот гайд — о том, что "
          "для этого нужно, как это устроено в Kai и где проходят границы."),
    tldr_title="Коротко / TL;DR",
    tldr=[
        "Нужны три вещи: https-адрес API на публичном хосте, способ авторизации (OAuth 2.0, API-ключ, bearer или basic) и эндпоинт "
        "списка воронок. Остальное — по мере надобности.",
        "Подключение — спецификацией коннектора: JSON, который Kai сам набросает по документации или соберёт по шагам в чате. Писать "
        "код не нужно.",
        "После подключения агент работает с твоей CRM как с amoCRM: воронки и этапы, сделки, контакты, компании, задачи, заметки, поля, "
        "аналитика; события из CRM — в правила «событие → действие».",
        "Проверить заранее можно на Kai Sandbox CRM — тестовой CRM на стороне Kai, которая подключается как настоящая.",
        "Безопасность: только https, запросы только на хост твоего API, секреты зашифрованы, шаблоны без кода, лимиты на размер и частоту.",
        "Подключение своей CRM — на тарифе Max (€119/мес). Обсудить систему и составить спецификацию можно бесплатно.",
    ],
    body='''
<h2>Что такое «своя CRM» для ИИ-агента</h2>
<p>«Своя» здесь — любая CRM, которой нет в списке готовых интеграций: самописная система на Laravel или Django, кастомная сборка на базе открытой CRM вроде EspoCRM или SuiteCRM, внутренний портал с модулем продаж, зарубежная CRM вроде HubSpot или Pipedrive. Агенту всё равно, на чём она написана. Ему важны три вещи: куда слать запросы, как подтвердить, что это ты, и какой запрос за что отвечает. В Kai всё это описывается спецификацией коннектора — JSON на несколько десятков строк. Для HubSpot, Pipedrive и EspoCRM готовые спецификации уже лежат в <a href="__DOCS__">документации</a>: вставил, подставил токен, отправил.</p>

<h2>Что понадобится до подключения</h2>
<ul>
  <li><strong>Базовый адрес API</strong> — только https и только публичный хост. Локальные адреса, внутренние сети и адреса облачных метаданных Kai отклоняет: так через агента нельзя достучаться до чужой инфраструктуры.</li>
  <li><strong>Авторизация</strong> одним из способов: OAuth 2.0 (authorization code с PKCE или client credentials), bearer-токен, API-ключ в заголовке или basic. Это покрывает то, что умеет большинство самописных API.</li>
  <li><strong>Эндпоинт списка воронок с этапами</strong> — единственная обязательная операция. Сделки, контакты, задачи, заметки, поля, пользователи — по желанию: описал — агент умеет, не описал — честно скажет, что для этой CRM операция недоступна, и подскажет, что добавить.</li>
  <li><strong>Ответы в JSON.</strong> XML и HTML коннектор не принимает.</li>
  <li><strong>Человек, который знает систему.</strong> Kai набрасывает спецификацию по описанию, но имена полей должен проверить тот, кто видел код или документацию.</li>
</ul>

<h2>Три способа подключить</h2>
<ol>
  <li><strong>Песочница.</strong> В чате Kai — в Telegram или в браузере — нажми «🔗 Подключить CRM» → «🔧 Своя CRM по API» → «🧪 Попробовать на песочнице Kai». Kai поднимает у себя небольшую тестовую CRM с воронками, сделками, задачами и подписанными событиями и подключает её как настоящую «свою». Всё, что описано ниже, работает и там — самый быстрый способ увидеть, что агент будет делать с твоей системой, не написав ни строки спецификации.</li>
  <li><strong>По документации.</strong> Вставь в чат несколько абзацев описания своего API или прикрепи файл — Kai составит черновик спецификации, ты проверишь имена полей и отправишь обратно.</li>
  <li><strong>По шагам.</strong> Кнопка «🧩 Собрать спецификацию по шагам»: Kai спрашивает адрес API, способ авторизации и два пути — воронки и сделки, сам вызывает их и читает имена полей из живых ответов. JSON писать не нужно; с OAuth 2.0 поля читаются сразу после авторизации.</li>
</ol>
<p>Готовый JSON можно прислать и текстом, и файлом .json. Перед сохранением Kai проверяет спецификацию — https, публичный хост, плейсхолдеры, секреты — и говорит, что именно поправить. Для OAuth 2.0 после этого появится кнопка «Авторизоваться» на стороне твоей CRM; для остальных способов Kai сразу вызывает список воронок и показывает, что увидел. Между несколькими CRM переключаются командой <kbd>/accounts</kbd>.</p>
<div class="note">Минимальная спецификация — название, базовый адрес, блок авторизации и одна операция <kbd>pipelines.list</kbd> с путями к полям ответа. С ней уже можно подключиться и увидеть свои воронки; остальное добавляется позже. Шаблон и примеры — в <a href="__DOCS__">документации Kai</a>.</div>

<h2>Что умеет агент после подключения</h2>
<div class="table-wrap">
<table>
  <thead><tr><th>Операция</th><th>Что делает Kai</th><th>Что описать в спецификации</th></tr></thead>
  <tbody>
    <tr><td>Воронки и этапы</td><td>Показывает, создаёт, переименовывает, добавляет этапы; различает этапы «успех» и «отказ»</td><td>pipelines.list — обязательно; create, update, add_stage — по желанию</td></tr>
    <tr><td>Сделки</td><td>Ищет, создаёт, обновляет, переводит по этапам, привязывает контакты и компании</td><td>leads.list, leads.search, leads.create, leads.update</td></tr>
    <tr><td>Контакты и компании</td><td>Создаёт и обновляет из сообщения или голосового</td><td>contacts.*, companies.*</td></tr>
    <tr><td>Задачи</td><td>Ставит с дедлайном по сделке, закрывает; читает список — для «здоровья сделки» и брифа к встрече</td><td>tasks.create, tasks.complete, tasks.list</td></tr>
    <tr><td>Заметки и теги</td><td>Добавляет заметки, вешает теги</td><td>notes.create, notes.list, tags.*</td></tr>
    <tr><td>Поля</td><td>Создаёт поля сделок, контактов и компаний: текст, число, список, дата; заполняет значения</td><td>fields.*</td></tr>
    <tr><td>Аналитика воронки</td><td>Сколько сделок на каждом этапе, где застревают</td><td>Данные из leads.list</td></tr>
    <tr><td>Автоматизации</td><td>Правила «событие → действие»: твоя CRM шлёт событие на вебхук Kai, он ставит задачу, пишет заметку, уведомляет в чат</td><td>Блок events в спецификации + вебхук из твоей CRM, подпись HMAC по желанию</td></tr>
  </tbody>
</table>
</div>
<p>Плейсхолдеры вида <kbd>{{name}}</kbd> в путях и телах запросов заполняются из параметров действия, <kbd>{{secret.token}}</kbd> — из секретов этого коннектора. Пути к данным в ответе точечные: <kbd>data.items</kbd>, <kbd>result.0.id</kbd>. Агент собирает запросы только из того, что ты описал: ни кода, ни доступа к чему-то ещё.</p>

<h2>Безопасность: чего агент не сможет сделать с твоей системой</h2>
<ul>
  <li>Только https и только публичные хосты: адреса проверяются и при сохранении спецификации, и перед каждым запросом — DNS разрешается заново.</li>
  <li>Запросы уходят только на хост из базового адреса: пути в спецификации относительные, абсолютные адреса и редиректы запрещены.</li>
  <li>Шаблоны — не код: только плейсхолдеры. Доступа к окружению Kai, базе или другим пользователям у них нет.</li>
  <li>Секреты хранятся зашифрованными, не попадают в логи и вырезаются из текстов ошибок.</li>
  <li>Лимиты: спецификация до 64 КБ, тело запроса до 256 КБ, ответ до 1 МБ, таймаут 15 секунд, 60 вызовов в минуту на коннектор.</li>
  <li>OAuth 2.0: подписанный state на 15 минут, PKCE, фиксированный redirect URI; код меняется на токен только на сервере Kai.</li>
</ul>
<p>Отозвать доступ можно в любой момент — удали токен или ключ на стороне своей CRM, и следующий запрос агента просто не пройдёт.</p>

<h2>Границы: чего не будет</h2>
<ul>
  <li>Виджетов и кнопок внутри твоей CRM: агент живёт в чате и работает через API, в интерфейс системы он ничего не добавляет.</li>
  <li>Операций, которых нет в спецификации: Kai не угадывает эндпоинты, он просит их описать.</li>
  <li>Работы с API без JSON, с нестандартной подписью запросов или только во внутренней сети — тут сначала нужен разработчик.</li>
</ul>

<h2>Когда нужен разработчик</h2>
<ul>
  <li>У CRM нет API — его придётся написать. Минимум: список воронок и сделок, остальное по шагам.</li>
  <li>API есть, но только в локальной сети — нужен публичный https-эндпоинт с авторизацией.</li>
  <li>Нужны события из CRM для автоматизаций — CRM надо научить слать вебхук на адрес Kai: один POST с JSON.</li>
</ul>
<p>В остальных случаях разработчик не нужен: спецификацию составляет Kai, проверяет тот, кто знает систему.</p>

<h2>С Kai это одно сообщение</h2>
<p>После подключения разговор про свою CRM ничем не отличается от разговора про amoCRM: описываешь, что нужно, Kai уточняет, показывает план, делает и присылает отчёт. Примеры:</p>
<pre>Покажи воронки в моей CRM и сколько сделок на каждом этапе.</pre>
<pre>Создай сделку «Петров, кухня» на 350 000 в воронке «Продажи», контакт Петров, телефон +7 900 000-00-00, и задачу «перезвонить» на завтра.</pre>
<pre>Когда сделка переходит на этап «Договор» — ставь ответственному задачу «выставить счёт» и напиши мне в чат.</pre>
<p>Подключение своей CRM — на тарифе Max: €119/мес, до 10 CRM-аккаунтов, приоритетная поддержка. Обсудить систему, попросить черновик спецификации и задать вопросы можно бесплатно — в пробный период и на любом тарифе. Kai говорит по-русски и по-английски.</p>
''',
    faq_title="Частые вопросы",
    faq=[
        ("Моя CRM самописная, API есть, а документации нет. Получится?",
         "Да. Пришли примеры запросов и ответов или кусок кода контроллеров — Kai составит черновик спецификации. Или собери её по "
         "шагам: укажи адрес, способ авторизации и пути к воронкам и сделкам, Kai вызовет их и сам прочитает имена полей из ответов."),
        ("Безопасно ли давать ИИ-агенту доступ к своей CRM?",
         "Доступ ограничен тем, что описано в спецификации: запросы только на твой хост и только по https, шаблоны без кода, секреты "
         "зашифрованы, лимиты на размер и частоту. Отозвать доступ — удалить токен или ключ на своей стороне."),
        ("Сколько стоит подключение своей CRM?",
         "Это тариф Max — €119/мес, до 10 CRM-аккаунтов, приоритетная поддержка. Обсуждение и черновик спецификации бесплатны. "
         "Разработка самой CRM или её API в тариф не входит."),
        ("Подойдут ли HubSpot, Pipedrive или EspoCRM?",
         "Да. Для агента это такие же «свои CRM» по API: готовые спецификации для них есть в документации Kai, нужен только токен "
         "или API-ключ."),
    ],
    next_title="Что дальше",
    next=("Открой чат Kai, нажми «Подключить CRM» → «Своя CRM по API» и начни с песочницы или пришли документацию. Если у системы "
          "есть REST API, за вечер она становится CRM, которой можно управлять словами."),
    cta=("Попробовать в Telegram", "Открыть веб-чат", "Документация: своя CRM по API"),
    author=("Автор: Команда Kai · Обновлено <time datetime=\"2026-11-01\">1 ноября 2026</time> · Возможности описаны по состоянию "
            "на дату публикации; актуальный статус и шаблон спецификации Kai сообщает в чате и в документации."),
    footer=("Главная", "Конфиденциальность", "Условия", "English version"),
    policies=("privacy.html", "terms.html"),
    index_title="Как подключить ИИ-агента к самописной CRM: по API, без переписывания системы",
    index_desc=("Что нужно от вашей CRM (REST API с JSON, авторизация, список воронок), три способа подключить, что агент умеет "
                "после, безопасность и границы."),
)

EN = dict(
    lang="en",
    h1="How to connect an AI agent to a custom (in-house) CRM via its API — without rewriting the system",
    title_tag="AI agent for a custom CRM: how to connect it via the API without rewriting the system | Kai",
    og_title="How to connect an AI agent to a custom CRM via its API",
    desc=("What it takes for an AI agent to work with your own (custom, in-house) CRM: a REST API with JSON, OAuth 2.0 / API key / "
          "bearer auth and a connector spec. Three ways to connect, what the agent can do afterwards, the limits and the security "
          "model — using Kai as the example."),
    og_desc=("A custom CRM with a REST API connects to an AI agent without a rewrite: the API address, the auth method, a pipelines "
             "list — and then pipelines, deals, tasks and automations in plain words. What you need, how to connect, where the limits are."),
    keywords=("connect AI agent to custom CRM, AI assistant for in-house CRM, homegrown CRM AI integration, CRM REST API AI agent, "
              "bespoke CRM AI, your own CRM via API"),
    author_meta="Kai team",
    meta="Updated 1 November 2026 · Kai team · 8 min read",
    crumb="AI agent for a custom CRM",
    crumbs_label="Breadcrumbs",
    nav=("Website", "Telegram bot", "RU"),
    guides_label="Guides",
    lead=("Many companies run their own CRM: written for their process, hosted on their own server, and no off-the-shelf “AI assistant "
          "for amoCRM” fits it. You don't need to rewrite the system for that. If the CRM has a REST API that answers in JSON, an AI "
          "agent connects to it the same way it connects to a boxed one: you describe where the API lives, how to authorize and which "
          "request does what, and then you set up pipelines, create tasks and automations in plain words in a chat. This guide covers "
          "what you need, how it works in Kai and where the limits are."),
    tldr_title="In short / TL;DR",
    tldr=[
        "Three things are needed: an https API address on a public host, an auth method (OAuth 2.0, API key, bearer or basic) and a "
        "pipelines-list endpoint. Everything else is optional.",
        "You connect with a connector spec: a JSON that Kai drafts from your docs or builds step by step in the chat. No code to write.",
        "After that the agent works with your CRM like with amoCRM: pipelines and stages, deals, contacts, companies, tasks, notes, "
        "fields, analytics; events from your CRM feed “event → action” rules.",
        "Try it first on Kai Sandbox CRM — a test CRM on Kai's side that connects exactly like a real one.",
        "Security: https only, requests only to your API's host, encrypted secrets, templates without code, size and rate limits.",
        "Connecting your own CRM is on the Max plan (€119/mo). Discussing the system and drafting the spec is free.",
    ],
    body='''
<h2>What “your own CRM” means to an AI agent</h2>
<p>“Your own” here is any CRM that isn't on the list of ready-made integrations: an in-house system on Laravel or Django, a custom build on top of an open-source CRM such as EspoCRM or SuiteCRM, an internal portal with a sales module, or a CRM like HubSpot or Pipedrive. The agent doesn't care what it's written in. It needs three things: where to send requests, how to prove it's you, and which request does what. In Kai all of this is a connector spec — a JSON of a few dozen lines. Ready-made specs for HubSpot, Pipedrive and EspoCRM are already in the <a href="__DOCS__">docs</a>: paste, put your token in, send.</p>

<h2>What you need before connecting</h2>
<ul>
  <li><strong>The base URL of the API</strong> — https only and a public host only. Kai rejects local addresses, private networks and cloud metadata addresses, so nobody can reach someone else's infrastructure through the agent.</li>
  <li><strong>Authorization</strong> in one of these ways: OAuth 2.0 (authorization code with PKCE or client credentials), a bearer token, an API key in a header, or basic auth. That covers what most in-house APIs can do.</li>
  <li><strong>A pipelines-with-stages endpoint</strong> — the only mandatory operation. Deals, contacts, tasks, notes, fields, users are optional: describe them and the agent can use them; leave them out and it will honestly say the operation isn't available for this CRM and tell you what to add.</li>
  <li><strong>JSON responses.</strong> The connector doesn't accept XML or HTML.</li>
  <li><strong>Someone who knows the system.</strong> Kai drafts the spec from a description, but the field names should be checked by a person who has seen the code or the docs.</li>
</ul>

<h2>Three ways to connect</h2>
<ol>
  <li><strong>Sandbox.</strong> In the Kai chat — Telegram or browser — tap “🔗 Connect CRM” → “🔧 My own CRM via API” → “🧪 Try Kai Sandbox CRM”. Kai spins up a small test CRM on its side with pipelines, deals, tasks and signed events and connects it exactly like a real custom CRM. Everything below works there too — the fastest way to see what the agent will do with your system before writing a line of the spec.</li>
  <li><strong>From the docs.</strong> Paste a few paragraphs describing your API into the chat or attach a file — Kai drafts the spec, you check the field names and send it back.</li>
  <li><strong>Step by step.</strong> The “🧩 Build the spec step by step” button: Kai asks for the API address, the auth method and two paths — pipelines and deals — calls them itself and reads the field names from live responses. No JSON to write; with OAuth 2.0 the fields are read right after you authorize.</li>
</ol>
<p>A ready JSON can be sent as text or as a .json file. Before saving, Kai validates the spec — https, public host, placeholders, secrets — and tells you exactly what to fix. For OAuth 2.0 an “Authorize” button then appears for your CRM's side; for the other methods Kai calls the pipelines list right away and shows what it sees. Switch between several CRMs with <kbd>/accounts</kbd>.</p>
<div class="note">A minimal spec is a name, the base URL, the auth block and one <kbd>pipelines.list</kbd> operation with the paths to the response fields. That's enough to connect and see your pipelines; the rest can be added later. The template and examples are in the <a href="__DOCS__">Kai docs</a>.</div>

<h2>What the agent can do once connected</h2>
<div class="table-wrap">
<table>
  <thead><tr><th>Operation</th><th>What Kai does</th><th>What to describe in the spec</th></tr></thead>
  <tbody>
    <tr><td>Pipelines and stages</td><td>Lists, creates, renames, adds stages; tells “won” and “lost” stages apart</td><td>pipelines.list — mandatory; create, update, add_stage — optional</td></tr>
    <tr><td>Deals</td><td>Searches, creates, updates, moves between stages, links contacts and companies</td><td>leads.list, leads.search, leads.create, leads.update</td></tr>
    <tr><td>Contacts and companies</td><td>Creates and updates from a text or voice message</td><td>contacts.*, companies.*</td></tr>
    <tr><td>Tasks</td><td>Creates with a due date on a deal, completes; reads the list for deal health and meeting briefs</td><td>tasks.create, tasks.complete, tasks.list</td></tr>
    <tr><td>Notes and tags</td><td>Adds notes, applies tags</td><td>notes.create, notes.list, tags.*</td></tr>
    <tr><td>Fields</td><td>Creates deal, contact and company fields: text, number, list, date; sets values</td><td>fields.*</td></tr>
    <tr><td>Pipeline analytics</td><td>How many deals sit on each stage and where they get stuck</td><td>Data from leads.list</td></tr>
    <tr><td>Automations</td><td>“Event → action” rules: your CRM sends an event to Kai's webhook, Kai creates a task, writes a note, notifies the chat</td><td>The events block in the spec + a webhook from your CRM, HMAC signature optional</td></tr>
  </tbody>
</table>
</div>
<p>Placeholders like <kbd>{{name}}</kbd> in paths and request bodies are filled from the action's parameters, <kbd>{{secret.token}}</kbd> from this connector's secrets. Response paths are dotted: <kbd>data.items</kbd>, <kbd>result.0.id</kbd>. The agent builds requests only from what you described: no code, no access to anything else.</p>

<h2>Security: what the agent cannot do to your system</h2>
<ul>
  <li>https only and public hosts only: addresses are checked both when the spec is saved and before every request — DNS is resolved again.</li>
  <li>Requests go only to the host of the base URL: paths in the spec are relative, absolute URLs and redirects are forbidden.</li>
  <li>Templates are not code: placeholders only. They have no access to Kai's environment, database or other users.</li>
  <li>Secrets are stored encrypted, never logged and are redacted from error messages.</li>
  <li>Limits: spec up to 64 KB, request body up to 256 KB, response up to 1 MB, 15-second timeout, 60 calls per minute per connector.</li>
  <li>OAuth 2.0: a signed state valid for 15 minutes, PKCE, a fixed redirect URI; the code is exchanged for a token only on Kai's server.</li>
</ul>
<p>You can revoke access at any moment — delete the token or key on your CRM's side, and the agent's next request simply won't go through.</p>

<h2>Limits: what you won't get</h2>
<ul>
  <li>Widgets or buttons inside your CRM: the agent lives in the chat and works through the API; it adds nothing to the system's interface.</li>
  <li>Operations that aren't in the spec: Kai doesn't guess endpoints, it asks you to describe them.</li>
  <li>APIs without JSON, with a non-standard request signature or reachable only inside a private network — a developer is needed first.</li>
</ul>

<h2>When you need a developer</h2>
<ul>
  <li>The CRM has no API — it has to be written. The minimum: pipelines and deals lists; the rest step by step.</li>
  <li>There is an API, but only inside the local network — you need a public https endpoint with authorization.</li>
  <li>You want events from the CRM for automations — the CRM has to send a webhook to Kai's address: one POST with JSON.</li>
</ul>
<p>In every other case no developer is needed: Kai drafts the spec, the person who knows the system checks it.</p>

<h2>With Kai it's one message</h2>
<p>Once connected, talking about your CRM is no different from talking about amoCRM: you describe what you need, Kai asks follow-ups, shows a plan, does it and sends a report. Examples:</p>
<pre>Show the pipelines in my CRM and how many deals sit on each stage.</pre>
<pre>Create the deal “Peters, kitchen” for 3,500 in the “Sales” pipeline, contact Peters, phone +1 555 000-0000, and a task “call back” for tomorrow.</pre>
<pre>When a deal moves to the “Contract” stage — create the task “issue the invoice” for the owner and message me in the chat.</pre>
<p>Connecting your own CRM is on the Max plan: €119/mo, up to 10 CRM accounts, priority support. Discussing the system, asking for a draft spec and asking questions is free — during the trial and on any plan. Kai speaks English and Russian.</p>
''',
    faq_title="FAQ",
    faq=[
        ("My CRM is in-house, it has an API but no docs. Will it work?",
         "Yes. Send examples of requests and responses or a piece of the controller code — Kai drafts the spec. Or build it step by "
         "step: give the address, the auth method and the paths to pipelines and deals; Kai calls them and reads the field names from "
         "the responses itself."),
        ("Is it safe to give an AI agent access to my own CRM?",
         "Access is limited to what the spec describes: requests only to your host and only over https, templates without code, "
         "encrypted secrets, size and rate limits. To revoke access, delete the token or key on your side."),
        ("How much does connecting my own CRM cost?",
         "It's the Max plan — €119/mo, up to 10 CRM accounts, priority support. Discussion and a draft spec are free. Building the CRM "
         "itself or its API is not part of the plan."),
        ("Do HubSpot, Pipedrive or EspoCRM count?",
         "Yes. To the agent they are the same “own CRMs” via API: ready-made specs for them are in the Kai docs, you only need a token "
         "or an API key."),
    ],
    next_title="What's next",
    next=("Open the Kai chat, tap “Connect CRM” → “My own CRM via API” and start with the sandbox or send your docs. If the system has "
          "a REST API, in one evening it becomes a CRM you can run with words."),
    cta=("Try in Telegram", "Open web chat", "Docs: your own CRM via API"),
    author=("Author: Kai team · Updated <time datetime=\"2026-11-01\">1 November 2026</time> · Capabilities as of the publication "
            "date; the current status and the spec template are in the chat and the docs."),
    footer=("Home", "Privacy", "Terms", "Русская версия"),
    policies=("privacy-en.html", "terms-en.html"),
    index_title="How to connect an AI agent to a custom (in-house) CRM via its API",
    index_desc=("What your CRM needs (a REST API with JSON, auth, a pipelines list), three ways to connect, what the agent can do "
                "afterwards, security and limits."),
)


def a(s):
    return html.escape(s, quote=True)


def page(L):
    lang, en = L["lang"], L["lang"] == "en"
    url = BASE + ("guides/en/" if en else "guides/") + SLUG + ".html"
    alt_ru, alt_en = BASE + "guides/" + SLUG + ".html", BASE + "guides/en/" + SLUG + ".html"
    other = alt_ru if en else alt_en
    docs = DOCS + lang
    chat = "https://app.aii-crm.com/chat?lang=" + lang
    guides_url = BASE + ("guides/en/" if en else "guides/")
    tldr = "".join("    <li>%s</li>\n" % x for x in L["tldr"])
    faq = "".join('  <div class="faq-item">\n    <h3>%s</h3>\n    <p>%s</p>\n  </div>\n' % (q, ans) for q, ans in L["faq"])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": url + "#article", "headline": L["h1"], "description": L["desc"], "inLanguage": lang,
         "datePublished": DATE, "dateModified": DATE, "mainEntityOfPage": url, "image": BASE + "og-image-v5.png",
         "author": {"@type": "Organization", "name": "Kai", "url": BASE},
         "publisher": {"@type": "Organization", "name": "Kai", "url": BASE}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}}
                                            for q, ans in L["faq"]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Kai", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": L["guides_label"], "item": guides_url},
            {"@type": "ListItem", "position": 3, "name": L["og_title"], "item": url}]}]}
    head = (
        '<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n%s\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n'
        '<meta name="robots" content="index, follow">\n<meta name="author" content="%s">\n'
        '<link rel="canonical" href="%s">\n<link rel="alternate" hreflang="ru" href="%s">\n<link rel="alternate" hreflang="en" href="%s">\n'
        '<link rel="alternate" hreflang="x-default" href="%s">\n'
        '<meta property="og:type" content="article">\n<meta property="og:locale" content="%s">\n<meta property="og:locale:alternate" content="%s">\n'
        '<meta property="og:site_name" content="Kai">\n<meta property="og:url" content="%s">\n<meta property="og:title" content="%s">\n'
        '<meta property="og:description" content="%s">\n<meta property="og:image" content="%sog-image-v5.png">\n'
        '<meta property="article:published_time" content="%s">\n<meta property="article:modified_time" content="%s">\n'
        '<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n<meta name="twitter:image" content="%sog-image-v5.png">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">\n'
        '%s\n</head>\n'
    ) % (lang, HW, a(L["title_tag"]), a(L["desc"]), a(L["keywords"]), a(L["author_meta"]), url, alt_ru, alt_en, alt_ru,
         "en_US" if en else "ru_RU", "ru_RU" if en else "en_US", url, a(L["og_title"]), a(L["og_desc"]), BASE, DATE, DATE,
         a(L["og_title"]), a(L["og_desc"]), BASE, CSS)
    body = (
        '<body>\n<header class="header">\n  <div class="header-in">\n'
        '    <a class="brand" href="%s" aria-label="Kai — %s">\n'
        '      <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M39.21 19.58A15.84 15.84 0 1 1 23.5 8.17" fill="none" stroke="var(--accent)" '
        'stroke-width="6.72" stroke-linecap="round"/><circle cx="33.12" cy="11.44" r="3.36" fill="var(--accent-2)"/></svg>\n      Kai\n    </a>\n'
        '    <nav class="nav" aria-label="%s">\n      <a href="%s">%s</a>\n      <a href="https://t.me/aiicrm_bot">%s</a>\n'
        '      <a href="%s" hreflang="%s">%s</a>\n    </nav>\n  </div>\n</header>\n\n<main>\n<article>\n'
        '<nav class="crumbs" aria-label="%s">\n  <a href="%s">Kai</a> › <a href="%s">%s</a> › %s\n</nav>\n\n'
        '<h1>%s</h1>\n<p class="meta">%s</p>\n\n<p class="lead">%s</p>\n\n'
        '<section class="tldr" aria-label="%s">\n  <h2>%s</h2>\n  <ul>\n%s  </ul>\n</section>\n'
        '%s\n<h2>%s</h2>\n<div class="faq">\n%s</div>\n\n<h2>%s</h2>\n<p>%s</p>\n<div class="cta">\n'
        '  <a class="btn btn-primary" href="https://t.me/aiicrm_bot">%s</a>\n  <a class="btn btn-secondary" href="%s">%s</a>\n'
        '  <a class="btn btn-secondary" href="%s">%s</a>\n</div>\n\n<p class="author">%s</p>\n</article>\n</main>\n\n'
        '<footer>\n  © 2026 Kai · <a href="%s">%s</a> · <a href="%s%s">%s</a> · <a href="%s%s">%s</a> · <a href="%s">%s</a>\n</footer>\n\n'
        '<script type="application/ld+json">\n%s\n</script>\n</body>\n</html>\n'
    ) % (BASE + ("en/" if en else ""), "home" if en else "на главную", "Navigation" if en else "Навигация",
         BASE + ("en/" if en else ""), L["nav"][0], L["nav"][1], other, "ru" if en else "en", L["nav"][2],
         L["crumbs_label"], BASE + ("en/" if en else ""), guides_url, L["guides_label"], L["crumb"],
         L["h1"], L["meta"], L["lead"], "In short" if en else "Коротко", L["tldr_title"], tldr,
         L["body"].replace("__DOCS__", docs), L["faq_title"], faq, L["next_title"], L["next"],
         L["cta"][0], chat, L["cta"][1], docs, L["cta"][2], L["author"],
         BASE + ("en/" if en else ""), L["footer"][0], BASE, L["policies"][0], L["footer"][1], BASE, L["policies"][1], L["footer"][2],
         other, L["footer"][3], json.dumps(ld, ensure_ascii=False, indent=2))
    return head + body


entry = {"slug": SLUG, "title_ru": RU["index_title"], "title_en": EN["index_title"], "desc_ru": RU["index_desc"],
         "desc_en": EN["index_desc"], "html_ru": page(RU), "html_en": page(EN),
         "prompts": ["подключить ИИ-агента к самописной CRM", "ИИ для кастомной CRM по API", "connect AI agent to custom CRM"]}
guides = [g for g in guides if g["slug"] != SLUG]
pos = next(i for i, g in enumerate(guides) if g["slug"] == "bitrix24-ai-assistant") + 1
guides.insert(pos, entry)
indent = None
if RAW.startswith("[\n"):
    indent = len(RAW.split("\n")[1]) - len(RAW.split("\n")[1].lstrip())
io.open(GUIDES, "w", encoding="utf-8", newline="\n").write(json.dumps(guides, ensure_ascii=False, indent=indent) + ("\n" if RAW.endswith("\n") else ""))
print("guide %s: ru %d KB, en %d KB, position %d of %d" % (SLUG, len(entry["html_ru"]) // 1024, len(entry["html_en"]) // 1024, pos + 1, len(guides)))
