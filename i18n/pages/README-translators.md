# Translating the second-level pages of aii-crm.com

Kai (aii-crm.com) is an AI assistant that configures CRM systems (amoCRM, Kommo, Bitrix24, custom CRMs) from a chat
message in Telegram or the browser. The landing page already exists in your language (dictionary `i18n/<lang>.json`).
These files translate the second-level pages: 9 guides, the guides index, the "before → after" examples page and the
three legal pages (privacy, terms, refund).

## Input and output

Input: `i18n/pages/src-*.json` — `{"<page>": ["English string", ...]}`. Strings are listed in page order, so the
neighbours give you context (a stage name, a table cell, a button label).

Output: one file per source file, `i18n/pages/<lang>-<chunk>.json` (for example `de-guides-a.json` for
`src-guides-a.json`). UTF-8, valid JSON:

```json
{"lang": "de", "strings": {"<English string exactly as in the source>": "<translation>", "...": "..."}}
```

Every string of every page in the source file must appear as a key. Keys are copied byte for byte: same HTML tags,
same quotes (“ ” " '), same entities (`&amp;`), same spaces, newlines written as `\n`. A string that appears in several
pages needs one key only.

## Hard rules — a violation makes the build fall back to English for that string

1. HTML tags inside a string stay exactly as they are: same tags, same order, same attributes, nothing added or
   removed. Translate only the text between and around them. Links, `href`, class names, `mailto:`, URLs: untouched.
2. Every number survives as the same digits: prices (€29, €59, €119), dates (2026; "September 24, 2026" becomes the
   local date format with the same digits), durations ("6 min read", "1–2 hours", "3–5 weeks"), percentages, GDPR article
   references (Art. 6(1)(b)). Never spell a number out, never add one.
3. Not translated: Kai, amoCRM, Kommo, Bitrix24, Telegram, Telegram Stars, USDT, OAuth, API, REST, JSON, product
   names (Albato, ApiX-Drive, Make, Zapier, n8n, Salebot, amoAI, HubSpot, Pipedrive, EspoCRM, SuiteCRM, Laravel, Django,
   Excel, CSV, Google Sheets, Apple Pay, Google Pay), @aiicrm_bot, e-mail addresses, cookie names and anything inside
   `<code>` tags.
4. CRM interface paths inside `<kbd>` stay in English (they reproduce the English UI of amoCRM/Kommo); a Russian path
   inside `<kbd>` stays Russian.
5. Multi-line strings (example messages to Kai, written with `\n`) keep their line breaks in the same places.
6. Valid JSON only: escape `"` as `\"` and `\` as `\\` inside values, newlines as `\n`; no comments, no trailing commas.

## Style

- Guides and examples: the tone of the landing dictionary (`i18n/<lang>.json`) — natural, idiomatic, the way a good
  tech blog about CRM would write in your language, not word for word. Headlines, `<title>` strings (ending with
  "| Kai") and meta descriptions must read like native search queries: this is SEO text. The "keywords" strings
  (comma-separated lists) are rewritten as the terms a business owner in your language would type into Google (keep the
  brand names, 10–20 items).
- Legal pages (privacy, terms, refund): formal legal register, precise and consistent terminology, the established GDPR
  vocabulary of your language (controller, processor, legal basis, data subject rights). Keep the section numbering.
- Terminology must match the landing: before translating, grep `i18n/<lang>.json` for pipeline, stage, field,
  required field, deal / lead, contact, task, automation / rule, tag, integrator, trial, plan (Start / Pro / Max),
  web chat, "before → after", and reuse those renderings.
- Short UI-like strings (stage names such as "New", "Booked"; field names; button labels "Try in Telegram", "Open web
  chat", "Copy the message") stay short, as a real CRM UI would show them.
- "Done." is the first word of Kai's replies on the examples page: translate it as one short word with a full stop and
  start every reply translation with exactly that word.

## How to work

1. Read the source file(s) fully. Skim 40 lines of `i18n/<lang>.json` strings to catch the tone and terms.
2. Translate page by page. Write the output file in parts so that no single write is huge: create the file with the
   first one or two pages (closing braces included), then insert the following pages' entries before the final closing
   braces with Edit — the file must be valid JSON after every step. Do not stop before every page is done.
3. When your files are complete, run from the repository root:

   ```
   PYTHONUTF8=1 py -3.12 i18n_pages.py check <lang> <your src files, e.g. src-guides-a src-cases>
   ```

   It reports missing, rejected (tag or digit mismatch) and unchanged keys for those pages. Fix every rejected and
   missing key and re-run until both are 0. "unchanged" lists long strings identical to English — fine only if they are
   genuinely untranslatable.
4. Do not modify any other file, do not run git, do not build pages.
5. Several translators work at the same time. Keep temporary helper scripts and backups only in your own folder
   (for example scratchpad/<lang>_<chunk>/), never under a shared name in a shared folder.

## Continuing after an interruption

If your output file already exists, never start over and never drop keys that are in it. Run

```
PYTHONUTF8=1 py -3.12 i18n_pages.py todo <lang> <src file, e.g. src-guides-b>
```

It writes `i18n/pages/todo-<lang>-<chunk>.json` with only the strings still missing (or rejected) for that source
file, page by page. Translate those and add them to your existing output file (Edit, inserting before the final
closing braces; a rejected key is replaced in place). Repeat todo/check until nothing is left, then delete your
todo file.
