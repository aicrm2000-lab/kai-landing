# -*- coding: utf-8 -*-
"""Второй уровень сайта на 10 языках (02.11.2026, Тихон: «чтобы полностью все переходы были на соответствующих языках»):
гайды guides/<lang>/<slug>.html, индекс гайдов guides/<lang>/, кейсы cases/<lang>/, политики privacy-<lang>.html,
terms-<lang>.html, refund-<lang>.html.

Источник — английские версии: html_en в guides.json, privacy-en/terms-en/refund-en.html, cases_data.py и словарь T в
build_cases.py, строки индекса гайдов (IX в build_guides.py). Переводы — словари i18n/pages/<lang>.json:
{"strings": {английский фрагмент: перевод}}. Фрагмент — содержимое блочного элемента (абзац, пункт списка, заголовок,
ячейка, pre) вместе с инлайновыми тегами внутри, плюс title/meta/aria-label и строки JSON-LD. Сборка подставляет
переводы по смещениям в исходный HTML (без перепарсинга), затем переписывает ссылки и hreflang на язык страницы.
Фрагмент без перевода или с другим набором тегов/цифр остаётся английским и считается.

Запуск:  py -3.12 i18n_pages.py extract        → i18n/pages/src-*.json (задания переводчикам)
         py -3.12 i18n_pages.py check [lang …] [src-guides-a …] → проверка словарей (можно только свои задания)
         py -3.12 i18n_pages.py todo <lang> <src-chunk> → i18n/pages/todo-<lang>-<chunk>.json, что осталось перевести
         py -3.12 i18n_pages.py build [lang …] → страницы на языках (их же вызывает build_guides.py)"""
import io
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://aii-crm.com/"
PAGES_DIR = os.path.join(HERE, "i18n", "pages")
LANGS = ["de", "fr", "es", "pl", "pt", "it", "tr", "be", "uk", "ro"]
ALL_LANGS = ["ru", "en"] + LANGS
LOCALES = {"ru": "ru_RU", "en": "en_US", "de": "de_DE", "fr": "fr_FR", "es": "es_ES", "pl": "pl_PL", "pt": "pt_BR", "it": "it_IT",
           "tr": "tr_TR", "be": "be_BY", "uk": "uk_UA", "ro": "ro_RO"}
POLICIES = ("privacy", "terms", "refund")

# Адреса страниц — по доменным окончаниям стран, а не по кодам языков (06.11.2026, Тихон): белорусский /by/, украинский /ua/.
# Код языка остаётся везде, где это язык (html lang, hreflang, inLanguage, og:locale, имена словарей i18n/<code>.json);
# slug — только в путях и ссылках. Подпись у флажка в меню языков — тот же slug заглавными (зеркало в index.html: KAI_LANG_SLUG).
# По старым адресам (be/, guides/be/…, privacy-be.html) сборка кладёт страницы-переадресации (write_redirect).
SLUGS = {"be": "by", "uk": "ua"}


def lang_slug(code: str) -> str:
    """код языка → окончание в адресе (be → by, uk → ua, остальные — как есть)"""
    return SLUGS.get(code, code)


def slug_lang(slug: str) -> str:
    """окончание в адресе → код языка (by → be, ua → uk)"""
    return next((c for c, s in SLUGS.items() if s == slug), slug)

INLINE = {"a", "b", "strong", "em", "i", "code", "span", "br", "kbd", "mark", "small", "sup", "sub", "abbr", "u", "s", "time", "wbr", "img"}
OPAQUE = {"script", "style", "svg", "noscript", "template"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
ATTRS = ("title", "alt", "aria-label", "placeholder")
META_KEYS = {("name", "description"), ("name", "keywords"), ("name", "twitter:title"), ("name", "twitter:description"),
             ("property", "og:title"), ("property", "og:description")}
LD_KEYS = {"headline", "description", "name", "text", "alternativeName"}
SKIP_EXACT = {"Kai", "Kai Team", "RU", "EN", "amoCRM", "Kommo", "Bitrix24", "@aiicrm_bot", "Telegram", "OAuth", "API", "FAQ", "©",
              "kai_vid", "kai_lang", "kai_cookie_consent", "→", "…", "Kai CRM", "Tsikhan Varabyou"}
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


# ---------------------------------------------------------------- дерево со смещениями
class Node:
    __slots__ = ("tag", "start", "cstart", "cend", "end", "children", "attrs", "raw")

    def __init__(self, tag, start, cstart):
        self.tag, self.start, self.cstart = tag, start, cstart
        self.cend = self.end = None
        self.children, self.attrs, self.raw = [], [], ""


class Tree(HTMLParser):
    def __init__(self, s: str):
        super().__init__(convert_charrefs=False)
        self.s = s
        self.lines = [0] + [m.end() for m in re.finditer("\n", s)]
        self.root = Node("#root", 0, 0)
        self.root.cend = self.root.end = len(s)
        self.stack = [self.root]
        self.feed(s)
        self.close()
        for n in self.stack[1:]:
            n.cend = n.end = len(s)

    def pos(self) -> int:
        line, off = self.getpos()
        return self.lines[line - 1] + off

    def handle_starttag(self, tag, attrs):
        p = self.pos()
        raw = self.get_starttag_text() or ""
        n = Node(tag, p, p + len(raw))
        n.attrs, n.raw = attrs, raw
        self.stack[-1].children.append(n)
        if tag in VOID or raw.endswith("/>"):
            n.cend = n.end = n.cstart
        else:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        p = self.pos()
        raw = self.get_starttag_text() or ""
        n = Node(tag, p, p + len(raw))
        n.attrs, n.raw = attrs, raw
        n.cend = n.end = n.cstart
        self.stack[-1].children.append(n)

    def handle_endtag(self, tag):
        p = self.pos()
        end = self.s.index(">", p) + 1
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                for n in self.stack[i + 1:]:
                    n.cend = n.end = p
                n = self.stack[i]
                n.cend, n.end = p, end
                del self.stack[i:]
                return


def _inline_only(n: Node) -> bool:
    return n.tag in INLINE and all(_inline_only(c) for c in n.children)


def _plain(text: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub("", text)).strip()


def _worth(text: str) -> bool:
    p = _plain(text)
    if not p or p in SKIP_EXACT:
        return False
    return re.search(r"[^\W\d_]", p) is not None


def _runs(n: Node, s: str, out: list) -> None:
    if n.tag in OPAQUE:
        return
    a, kids = n.cstart, []
    for ch in n.children:
        if _inline_only(ch):
            kids.append(ch)
            continue
        _flush(s, a, ch.start, out, kids)
        kids = []
        _runs(ch, s, out)
        a = ch.end
    _flush(s, a, n.cend, out, kids)


def _flush(s: str, a: int, b: int, out: list, kids: list = ()) -> None:
    text = s[a:b]
    if not _worth(text):
        return
    if len(kids) >= 2:   # только инлайновые элементы через пробелы (меню, кнопки) — каждый отдельным фрагментом
        gaps = s[a:kids[0].start] + "".join(s[k.end:k2.start] for k, k2 in zip(kids, kids[1:])) + s[kids[-1].end:b]
        if not _worth(gaps):
            for k in kids:
                _flush(s, k.cstart, k.cend, out, k.children)
            return
    ta = a + (len(text) - len(text.lstrip()))
    tb = b - (len(text) - len(text.rstrip()))
    out.append((ta, tb))


def _attr_segments(n: Node, s: str, out: list) -> None:
    if n.tag in OPAQUE:
        return
    if n.raw:
        wanted = list(ATTRS)
        if n.tag == "meta":
            d = dict(n.attrs)
            key = ("name", d["name"]) if "name" in d else (("property", d["property"]) if "property" in d else None)
            wanted = ["content"] if key in META_KEYS else []
        for a in wanted:
            m = re.search(rf'\s{re.escape(a)}="([^"]*)"', n.raw)
            if m and _worth(m.group(1)):
                out.append((n.start + m.start(1), n.start + m.end(1)))
    for ch in n.children:
        _attr_segments(ch, s, out)


def segments(s: str) -> list:
    """[(start, end)] переводимых фрагментов: содержимое блочных элементов (с инлайновыми тегами внутри) и атрибуты"""
    tree = Tree(s)
    runs, attrs = [], []
    _runs(tree.root, s, runs)
    _attr_segments(tree.root, s, attrs)
    inside = lambda a, b: any(ra <= a and b <= rb for ra, rb in runs)
    segs = runs + [(a, b) for a, b in attrs if not inside(a, b)]
    segs.sort()
    return segs


def ld_strings(s: str) -> list:
    """строки JSON-LD (headline/description/name/text) — переводятся отдельными ключами"""
    out = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            obj = json.loads(m.group(1))
        except ValueError:
            continue

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in LD_KEYS and isinstance(v, str) and _worth(v):
                        out.append(v)
                    else:
                        walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(obj)
    return out


# ---------------------------------------------------------------- словарь
class Dict:
    def __init__(self, data: dict):
        self.strings = data.get("strings", {})
        self.norm = {WS_RE.sub(" ", k).strip(): v for k, v in self.strings.items()}
        self.missing, self.rejected = [], []

    def t(self, en: str) -> str:
        if not _worth(en):
            return en
        v = self.strings.get(en)
        if v is None:
            v = self.norm.get(WS_RE.sub(" ", en).strip())
        if v is None or not v.strip():
            self.missing.append(en)
            return en
        if WS_RE.sub("", "".join(TAG_RE.findall(v))) != WS_RE.sub("", "".join(TAG_RE.findall(en))) or sorted(re.findall(r"\d+", v)) != sorted(re.findall(r"\d+", en)):
            self.rejected.append(en)
            return en
        return v


def dict_files(lang: str) -> list:
    """<lang>.json и части <lang>-*.json (переводчики пишут по кускам)"""
    if not os.path.isdir(PAGES_DIR):
        return []
    return sorted(os.path.join(PAGES_DIR, f) for f in os.listdir(PAGES_DIR) if f == f"{lang}.json" or (f.startswith(f"{lang}-") and f.endswith(".json")))


def load_dict(lang: str, policies: bool = False) -> "Dict | None":
    """все файлы языка в одном словаре; при совпадении ключей главнее policies-файл (policies=True, для страниц политик)
    или остальные файлы (по умолчанию, для гайдов и кейсов) — формальный и неформальный перевод одной строки не спорят"""
    files = dict_files(lang)
    if not files:
        return None
    is_pol = lambda f: os.path.basename(f).endswith("-policies.json")
    files = sorted(files, key=lambda f: is_pol(f) == policies)   # главный файл — последним
    strings = {}
    for p in files:
        strings.update(json.load(io.open(p, encoding="utf-8")).get("strings", {}))
    return Dict({"strings": strings})


def available_langs() -> list:
    return [c for c in LANGS if dict_files(c)]


_READY = {}


def is_ready(code: str) -> bool:
    """словарь переводит все строки всех страниц (без пропусков и отклонённых) — язык можно публиковать"""
    if code in ("ru", "en"):
        return True
    if code not in _READY:
        d = load_dict(code)
        if d is None:
            _READY[code] = False
        else:
            for k in (k for v in sources().values() for k in v):
                d.t(k)
            _READY[code] = not d.missing and not d.rejected
    return _READY[code]


def ready_langs() -> list:
    return [c for c in LANGS if dict_files(c) and is_ready(c)]


def translate_html(s: str, d: Dict, code: str) -> str:
    """подстановка переводов по смещениям + JSON-LD"""
    out = s
    for a, b in reversed(segments(s)):
        out = out[:a] + d.t(s[a:b]) + out[b:]

    def ld_sub(m):
        try:
            obj = json.loads(m.group(1))
        except ValueError:
            return m.group(0)

        def walk(o):
            if isinstance(o, dict):
                for k, v in list(o.items()):
                    if k in LD_KEYS and isinstance(v, str) and _worth(v):
                        o[k] = d.t(v)
                    elif k == "inLanguage" and isinstance(v, str):
                        o[k] = code
                    else:
                        walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(obj)
        return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>"
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld_sub, out, flags=re.S)


# ---------------------------------------------------------------- hreflang
def hreflang_block(path_for) -> str:
    """path_for(lang) → путь от корня; ru, en и готовые языки; x-default → английская версия"""
    lines = [f'<link rel="alternate" hreflang="{c}" href="{BASE}{path_for(c)}">' for c in ["ru", "en"] + ready_langs()]
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}{path_for("en")}">')
    return "\n".join(lines)


def set_hreflang(s: str, path_for) -> str:
    """убрать все прежние hreflang-ссылки и поставить один блок после canonical (повторная сборка ничего не задваивает)"""
    block = hreflang_block(path_for)
    s = re.sub(r'(?:<link rel="alternate" hreflang="[^"]+" href="[^"]+">\s*)+', "", s)   # прежние блоки (и задвоенные) — прочь
    return re.sub(r'(<link rel="canonical" href="[^"]+">\n?)', lambda m: m.group(1) + block + "\n", s, count=1)


def home_path(c: str) -> str:
    return "" if c == "ru" else f"{lang_slug(c)}/"


def guide_path(slug: str):
    return lambda c: f"guides/{slug}.html" if c == "ru" else f"guides/{lang_slug(c)}/{slug}.html"


def guides_index_path(c: str) -> str:
    return "guides/" if c == "ru" else f"guides/{lang_slug(c)}/"


def cases_path(c: str) -> str:
    return "cases/" if c == "ru" else f"cases/{lang_slug(c)}/"


def policy_path(kind: str):
    return lambda c: f"{kind}.html" if c == "ru" else f"{kind}-{lang_slug(c)}.html"


# ---------------------------------------------------------------- переадресация со старых адресов (be → by, uk → ua)
def redirect_html(new_path: str, code: str) -> str:
    """страница-переадресация: meta refresh 0 + canonical на новый адрес + noindex + location.replace (с ?query и #якорем)"""
    url = BASE + new_path
    return f"""<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<title>Kai</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace("/{new_path}" + location.search + location.hash);</script>
</head>
<body><a href="{url}">{url}</a></body>
</html>
"""


def write_redirect(old_path: str, new_path: str, code: str) -> None:
    """old_path, new_path — пути от корня ("be/", "guides/be/x.html"); каталог → index.html. Полная страница по старому
    адресу заменяется переадресацией; в sitemap и hreflang старые адреса не попадают (их строят path-функции выше)"""
    fp = os.path.join(HERE, *old_path.split("/"))
    if old_path.endswith("/"):
        fp = os.path.join(fp, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    io.open(fp, "w", encoding="utf-8", newline="\n").write(redirect_html(new_path, code))


# ---------------------------------------------------------------- гайды
def prep_guide_en(h: str, slug: str) -> str:
    """английский гайд как основа для других языков: переключатель RU → EN, «Русская версия» → «English version»"""
    h = re.sub(rf'<a href="{re.escape(BASE)}guides/{slug}\.html" hreflang="ru">RU</a>',
               f'<a href="{BASE}guides/en/{slug}.html" hreflang="en">EN</a>', h)
    h = h.replace(f'<a href="{BASE}guides/{slug}.html">Русская версия</a>', f'<a href="{BASE}guides/en/{slug}.html">English version</a>')
    return h


def relink_guide(h: str, slug: str, code: str) -> str:
    h = h.replace('<html lang="en">', f'<html lang="{code}">', 1)
    s = lang_slug(code)   # окончание в адресах (by, ua); code — язык (lang, og:locale)
    h = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n?', "", h)
    keep = {}

    def _keep(m):   # явные ссылки на русскую версию (hreflang="ru") не трогаем
        keep[f"\x00{len(keep)}\x00"] = m.group(0)
        return f"\x00{len(keep) - 1}\x00"
    h = re.sub(rf'href="{re.escape(BASE)}guides/[a-z0-9-]+\.html" hreflang="ru"', _keep, h)
    h = h.replace(f"{BASE}guides/en/", f"{BASE}guides/{s}/")
    h = re.sub(rf'{re.escape(BASE)}guides/([a-z0-9-]+)\.html', rf"{BASE}guides/{s}/\1.html", h)   # русские кросс-ссылки
    for k, v in keep.items():
        h = h.replace(k, v)
    h = h.replace(f'{BASE}guides/"', f'{BASE}guides/{s}/"')
    h = h.replace(f'{BASE}en/"', f'{BASE}{s}/"').replace(f'{BASE}"', f'{BASE}{s}/"')
    h = h.replace(f"{BASE}cases/en/", f"{BASE}cases/{s}/").replace(f'{BASE}cases/"', f'{BASE}cases/{s}/"')
    for p in POLICIES:
        h = h.replace(f"{BASE}{p}-en.html", f"{BASE}{p}-{s}.html").replace(f'{BASE}{p}.html', f"{BASE}{p}-{s}.html")
    h = h.replace('<meta property="og:locale" content="en_US">', f'<meta property="og:locale" content="{LOCALES[code]}">')
    h = h.replace('<meta property="og:locale:alternate" content="ru_RU">',
                  '<meta property="og:locale:alternate" content="en_US">\n<meta property="og:locale:alternate" content="ru_RU">')
    h = re.sub(r'(<link rel="canonical" href="[^"]+">\n?)', lambda m: m.group(1) + hreflang_block(guide_path(slug)) + "\n", h, count=1)
    # переключатель EN в шапке и «English version» в подвале — на английскую версию, а не на себя
    h = h.replace(f'<a href="{BASE}guides/{s}/{slug}.html" hreflang="en">EN</a>', f'<a href="{BASE}guides/en/{slug}.html" hreflang="en">EN</a>')
    h = re.sub(r"(<footer>(?:(?!</footer>).)*?)" + re.escape(f"{BASE}guides/{s}/{slug}.html"),
               lambda m: m.group(1) + f"{BASE}guides/en/{slug}.html", h, count=1, flags=re.S)
    return h


# ---------------------------------------------------------------- политики
DISCLAIMER = "This translation is provided for convenience. If it differs from the English text, the English version prevails."


def prep_policy_en(h: str, kind: str) -> str:
    """английская политика как основа: переключатель RU → EN, «Russian version» → «English version» (абсолютные ссылки на
    английскую версию — относительные href переписывает relink_policy), после подзаголовка — оговорка о переводе"""
    h = h.replace(f'<a href="{kind}.html" class="nav-lang">RU</a>', f'<a href="{BASE}{kind}-en.html" class="nav-lang">EN</a>', 1)
    h = re.sub(rf'<a href="{kind}\.html"([^>]*)>Russian version</a>', rf'<a href="{BASE}{kind}-en.html"\1>English version</a>', h)
    h = re.sub(r'(<p class="subtitle">.*?</p>\n)', lambda m: m.group(1) + f'<p class="subtitle">{DISCLAIMER}</p>\n', h, count=1, flags=re.S)
    return h


def set_policy_og(h: str, kind: str, code: str) -> str:
    """Open Graph политики из её (уже переведённых) <title> и description; прежние og-теги заменяются"""
    h = re.sub(r'<meta (?:property="og:[a-z_:]+"|name="twitter:[a-z]+") content="[^"]*">\n?', "", h)
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', h)
    if not t or not d:
        return h
    url = BASE + policy_path(kind)(code)
    og = (f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Kai">\n'
          f'<meta property="og:url" content="{url}">\n<meta property="og:locale" content="{LOCALES[code]}">\n'
          f'<meta property="og:title" content="{attr_q(t.group(1).strip())}">\n<meta property="og:description" content="{d.group(1)}">\n'
          f'<meta property="og:image" content="{BASE}og-image-v5.png">\n<meta name="twitter:card" content="summary_large_image">\n')
    return re.sub(r'(<link rel="canonical" href="[^"]+">\n)', lambda m: m.group(1) + og, h, count=1)


def attr_q(v: str) -> str:
    return v.replace('"', "&quot;")


def relink_policy(h: str, kind: str, code: str) -> str:
    h = h.replace('<html lang="en">', f'<html lang="{code}">', 1)
    s = lang_slug(code)
    h = h.replace('href="index.html#pricing"', f'href="{s}/#pricing"').replace('href="index.html"', f'href="{s}/"')
    for p in POLICIES:
        h = h.replace(f'href="{p}-en.html"', f'href="{p}-{s}.html"')
    h = h.replace(f'<link rel="canonical" href="{BASE}{kind}-en.html">', f'<link rel="canonical" href="{BASE}{kind}-{s}.html">')
    if "<link rel=\"canonical\"" not in h:
        h = h.replace('<meta name="robots"', f'<link rel="canonical" href="{BASE}{kind}-{s}.html">\n<meta name="robots"', 1)
    h = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n?', "", h)
    h = re.sub(r'(<link rel="canonical" href="[^"]+">\n?)', lambda m: m.group(1) + hreflang_block(policy_path(kind)) + "\n", h, count=1)
    h = h.replace("var LANG=document.documentElement.lang||'ru';", f"var LANG='{code}';")
    return set_policy_og(h, kind, code)


def policy_en(kind: str) -> str:
    """английская политика как исходник переводов — с исходными title/description (короткие для выдачи накладывает
    seo_meta поверх файла, а ключи переводов от них не должны зависеть)"""
    h = io.open(os.path.join(HERE, f"{kind}-en.html"), encoding="utf-8").read()
    p = os.path.join(HERE, "i18n", "seo", "originals.json")
    orig = json.load(io.open(p, encoding="utf-8")).get(f"{kind}-en.html") if os.path.exists(p) else None
    if orig:
        import html as _html
        h = re.sub(r"<title>.*?</title>", lambda _: f"<title>{_html.escape(orig['title'], quote=False)}</title>", h, count=1, flags=re.S)
        h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + _html.escape(orig["description"], quote=False).replace('"', "&quot;") + m.group(2), h, count=1)
    # Open Graph политики строит set_policy_og из переведённых title/description — в исходнике переводов он не нужен
    return re.sub(r'<meta (?:property="og:[a-z_:]+"|name="twitter:[a-z]+") content="[^"]*">\n?', "", h)


# ---------------------------------------------------------------- источник для переводчиков
def _guides():
    return json.load(io.open(os.path.join(HERE, "guides.json"), encoding="utf-8"))


def page_strings(s: str) -> list:
    seen, out = set(), []
    for a, b in segments(s):
        k = s[a:b]
        if k not in seen:
            seen.add(k)
            out.append(k)
    for k in ld_strings(s):
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def sources() -> dict:
    """{'guides/<slug>': [...], 'guides/index': [...], 'cases': [...], 'policies/<kind>': [...]} — английские строки"""
    import build_cases
    import build_guides
    src = {}
    guides = _guides()
    for g in guides:
        keys = page_strings(prep_guide_en(g["html_en"], g["slug"]))
        for k in (g["title_en"], g["desc_en"]):
            if k not in keys:
                keys.append(k)
        src[f"guides/{g['slug']}"] = keys
    src["guides/index"] = [v for v in build_guides.IX["en"].values() if _worth(v)]
    cases = []

    def walk(o, en=False):
        if isinstance(o, dict):
            if "en" in o and "ru" in o:
                walk(o["en"], True)
            else:
                for v in o.values():
                    walk(v, en)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v, en)
        elif en and isinstance(o, str) and _worth(o) and o not in cases:
            cases.append(o)
    walk(build_cases.CASES)
    walk(build_cases.ACTION_LABELS)
    for v in build_cases.T["en"].values():
        if _worth(v) and v not in cases:
            cases.append(v)
    if "Done." not in cases:
        cases.append("Done.")
    src["cases"] = cases
    for kind in POLICIES:
        src[f"policies/{kind}"] = page_strings(prep_policy_en(policy_en(kind), kind))
    return src


def chunks(src: dict) -> dict:
    """задания переводчикам: файл → страницы"""
    return {
        "src-guides-a.json": [k for k in src if k.startswith("guides/") and k != "guides/index"][:5],
        "src-guides-b.json": [k for k in src if k.startswith("guides/") and k != "guides/index"][5:],
        "src-policies.json": [k for k in src if k.startswith("policies/")],
        "src-cases.json": ["cases", "guides/index"],
    }


def extract() -> None:
    os.makedirs(PAGES_DIR, exist_ok=True)
    src = sources()
    chunks_ = chunks(src)
    total = 0
    for name, pages in chunks_.items():
        data = {p: src[p] for p in pages}
        n = sum(len(v) for v in data.values())
        size = sum(len(x) for v in data.values() for x in v)
        total += size
        io.open(os.path.join(PAGES_DIR, name), "w", encoding="utf-8", newline="\n").write(json.dumps(data, ensure_ascii=False, indent=1))
        print(f"{name}: {len(pages)} pages, {n} strings, {size // 1024} KB")
    print(f"total {total // 1024} KB of English text")


# ---------------------------------------------------------------- проверка словарей
def check(code: str, only=None) -> bool:
    """проверка словаря; only — имена файлов-заданий (src-*.json), чтобы смотреть только свои страницы"""
    d = load_dict(code)
    if d is None:
        print(f"{code}: no dictionary")
        return False
    src = sources()
    pages = [p for name, ps in chunks(src).items() if not only or name in only or name[:-5] in only for p in ps]
    keys = [k for p in pages for k in src[p]]
    missing = [k for k in keys if d.t(k) == k and k in d.missing]
    d.missing, d.rejected = [], []
    rejected = [k for k in keys if (d.t(k) == k and k in d.rejected)]
    same = [k for k in keys if k in d.strings and d.strings[k] == k and len(_plain(k)) > 12]
    cyr = [] if code in ("uk", "be") else [k for k in keys if re.search(r"[А-Яа-яЁё]", d.strings.get(k, ""))]
    extra = len(set(d.strings) - set(keys))
    print(f"{code}: {len(keys)} keys, missing {len(set(missing))}, rejected {len(set(rejected))}, unchanged {len(same)}, cyrillic {len(cyr)}, extra {extra}")
    for k in sorted(set(missing))[:5]:
        print("   missing:", k[:90])
    for k in sorted(set(rejected))[:8]:
        print("   rejected:", k[:90])
        print("           :", d.strings[k][:90])
    for k in same[:5]:
        print("   unchanged:", k[:90])
    for k in cyr[:3]:
        print("   cyrillic:", d.strings[k][:90])
    return not missing and not rejected


def todo(code: str, chunk: str) -> None:
    """i18n/pages/todo-<lang>-<chunk>.json: {страница: [английские строки без перевода или с отклонённым переводом]}"""
    d = load_dict(code) or Dict({"strings": {}})
    src = sources()
    name = chunk if chunk.endswith(".json") else chunk + ".json"
    out, n = {}, 0
    for page in chunks(src)[name]:
        left = []
        for k in src[page]:
            d.missing, d.rejected = [], []
            if d.t(k) == k and (d.missing or d.rejected) and k not in left:
                left.append(k)
        if left:
            out[page] = left
            n += len(left)
    fn = os.path.join(PAGES_DIR, f"todo-{code}-{name[4:]}")
    io.open(fn, "w", encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{code} {name}: {n} strings left → {os.path.relpath(fn, HERE)}")


# ---------------------------------------------------------------- сборка
def build(code: str) -> None:
    import build_cases
    import build_guides
    d = load_dict(code)
    if d is None:
        print(f"{code}: no dictionary, skipped")
        return
    guides = _guides()
    s = lang_slug(code)
    out_dir = os.path.join(HERE, "guides", s)
    os.makedirs(out_dir, exist_ok=True)
    for g in guides:
        h = translate_html(prep_guide_en(g["html_en"], g["slug"]), d, code)
        h = relink_guide(h, g["slug"], code)
        io.open(os.path.join(out_dir, f"{g['slug']}.html"), "w", encoding="utf-8", newline="\n").write(h)
    io.open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n").write(build_guides.index_page(code, guides, d))
    os.makedirs(os.path.join(HERE, "cases", s), exist_ok=True)
    io.open(os.path.join(HERE, "cases", s, "index.html"), "w", encoding="utf-8", newline="\n").write(build_cases.page(code, d))
    dp = load_dict(code, policies=True)
    for kind in POLICIES:
        h = translate_html(prep_policy_en(policy_en(kind), kind), dp, code)
        h = relink_policy(h, kind, code)
        io.open(os.path.join(HERE, policy_path(kind)(code)), "w", encoding="utf-8", newline="\n").write(h)
    n_redirects = 0
    if s != code:   # старые адреса с кодом языка (guides/be/…, cases/be/, privacy-be.html) → переадресация на новые
        pairs = [(f"guides/{code}/{g['slug']}.html", guide_path(g["slug"])(code)) for g in guides]
        pairs += [(f"guides/{code}/", guides_index_path(code)), (f"cases/{code}/", cases_path(code))]
        pairs += [(f"{kind}-{code}.html", policy_path(kind)(code)) for kind in POLICIES]
        for old, new in pairs:
            write_redirect(old, new, code)
        n_redirects = len(pairs)
    print(f"{s}: {len(guides)} guides + index, cases, {len(POLICIES)} policies; missing {len(set(d.missing))}, rejected {len(set(d.rejected))}"
          + (f"; {n_redirects} redirects from old /{code}/ paths" if n_redirects else ""))
    for k in sorted(set(d.rejected))[:5]:
        print("   rejected:", k[:80])


def build_all(codes=None) -> list:
    """собрать готовые языки (или указанные) и обновить hreflang в русских и английских политиках"""
    codes = codes or ready_langs()
    for c in codes:
        build(c)
    for kind in POLICIES:
        for code in ("ru", "en"):
            fp = os.path.join(HERE, policy_path(kind)(code))
            h = io.open(fp, encoding="utf-8").read()
            io.open(fp, "w", encoding="utf-8", newline="\n").write(set_policy_og(set_hreflang(h, policy_path(kind)), kind, code))
    skipped = [c for c in available_langs() if c not in codes]
    if skipped:
        print("not ready (dictionary incomplete), not built:", ", ".join(skipped))
    return codes


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    codes = sys.argv[2:] or None
    if cmd == "extract":
        extract()
    elif cmd == "todo":   # todo <lang> <src-chunk> — что осталось перевести
        todo(codes[0], codes[1])
    elif cmd == "check":   # check [lang …] [src-guides-a …] — только указанные задания
        only = [a for a in (codes or []) if a.startswith("src-")]
        codes = [a for a in (codes or []) if not a.startswith("src-")]
        ok = all([check(c, only) for c in (codes or available_langs())])
        sys.exit(0 if ok else 1)
    elif cmd == "build":
        build_all(codes)
    else:
        print(__doc__)
