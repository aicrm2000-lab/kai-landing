# Short search titles and descriptions

Search engines show about 70 characters of a page title and about 155 of its description; Bing reports longer
ones as errors. The pages keep their full titles and descriptions everywhere else; these files hold the short
versions that replace `<title>` and `<meta name="description">` in search results.

Input: `todo-<lang>.json` — `{"<page path>": {"title": "<current>", "description": "<current>"}}`, only the fields
that are too long. Output: `<lang>.json`, same paths, same fields, your short versions. UTF-8, valid JSON.

Rules
- Title: at most 70 characters including the ` | Kai` ending (keep the ending when the current title has it).
- Description: 70 to 158 characters.
- Same facts as the current text, nothing new: no new numbers, prices or promises. Keep product names as they are
  (Kai, amoCRM, Kommo, Bitrix24, Telegram, API).
- Put the words people search for first (the CRM names, the task: pipeline, import, automation, AI assistant).
  Write as a native speaker would type it into Google, not word for word.
- Same tone as the page (guides informal, legal pages formal).
- The English and Russian short versions for the same pages are in `en.json` and `ru.json` (paths `guides/en/…`,
  `en/`, `privacy-en.html`), use them as a model of length and focus.

Check, from the repository root:

```
PYTHONUTF8=1 py -3.12 seo_meta.py apply
PYTHONUTF8=1 py -3.12 seo_meta.py audit <lang>
```

`audit` must report 0 pages for your language. Then delete your `todo-<lang>.json`. Touch no other files, no git.
