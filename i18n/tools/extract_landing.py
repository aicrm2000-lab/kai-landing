# -*- coding: utf-8 -*-
"""Собирает исходник для переводов лендинга: уникальные английские строки (с русской парой как контекстом),
мета/JSON-LD из build_en.py и UI-строки, которых нет в разметке. Пишет D:\\Claude\\kai-landing\\i18n\\source.json.
Идентификаторы действий (snake_case вроде create_pipeline) не переводятся и в список не попадают."""
import io, json, os, re, sys

ROOT = r"D:\Claude\kai-landing"
sys.path.insert(0, ROOT)
from build_en import EN_META, EN_LD  # noqa: E402

s = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
TAG = re.compile(r'<[a-zA-Z][\w-]*(?:[^>"]|"[^"]*")*>', re.S)
IDENT = re.compile(r"^(?:<span class='dot'></span>)?[a-z0-9_]+(?:\s*×\d+)?$")

items, seen = [], {}
PAIRS = [("data-ru", "data-en"), ("data-ru-title", "data-en-title"), ("data-ru-label", "data-en-label"),
         ("data-hw-ru", "data-hw-en"), ("data-ny-ru", "data-ny-en")]
for m in TAG.finditer(s):
    tag = m.group(0)
    for ru_a, en_a in PAIRS:
        en = re.search(r'\s' + en_a + r'="([^"]*)"', tag)
        if not en:
            continue
        en = en.group(1)
        ru = re.search(r'\s' + ru_a + r'="([^"]*)"', tag)
        ru = ru.group(1) if ru else ""
        if en in seen or IDENT.match(en) or not re.search(r"[A-Za-z]", en):
            continue
        seen[en] = True
        items.append({"en": en, "ru": ru, "where": en_a})

source = {
    "_note": ("Keys to translate: every item's 'en' (the 'ru' is only context). Keep HTML tags, entities and attribute values "
              "exactly as in 'en'. Keep numbers, prices, product names (Kai, amoCRM, Kommo, Bitrix24, Telegram, OAuth, API, PDF, Excel)."),
    "items": items,
    "meta": EN_META,
    "ld": EN_LD,
    "ui": {
        "lang_name": "English",
        "lang_label": "Language",
        "kai_note": "Kai itself speaks English and Russian; this site is in English to help you find your way.",
        "words": ["KAI", "CRM", "Sales", "Flow", "Growth", "Focus"],
        "words_ny": ["KAI", "{year}", "SNOW", "MERRY", "CHEERS", "JOY", "NOEL", "FROST", "GIFTS", "JINGLE", "COZY", "SANTA"],
        "theme_hw": "Halloween mode", "theme_ny": "Holiday mode", "turn_on": ": turn on", "turn_off": ": turn off",
        "actions_word": "actions",
    },
}
os.makedirs(os.path.join(ROOT, "i18n"), exist_ok=True)
io.open(os.path.join(ROOT, "i18n", "source.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(source, ensure_ascii=False, indent=1) + "\n")
print("items:", len(items), "chars:", sum(len(i["en"]) for i in items), "with markup:", sum("<" in i["en"] for i in items),
      "by attr:", {a: sum(i["where"] == a for i in items) for _, a in PAIRS})
