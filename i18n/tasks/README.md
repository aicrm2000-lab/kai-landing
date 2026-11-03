# Update: "free" → "trial", Bitrix24 no longer "beta"

The site no longer says the first 3 days are "free": it says the first 3 days are a **trial** (English "3-day trial",
Russian «3 дня триала»). Bitrix24 is no longer labelled "beta" anywhere; its real limits (no robots, no widgets
inside Bitrix24 yet) stay. You update one language end to end.

Wording for the trial in your language — never the word for "free" (kostenlos, gratuit, gratis, grátis, za darmo,
ücretsiz, бясплатна, безкоштовно, gratuit…) when it describes the 3 days:
de Testphase · fr essai · es prueba · pt teste · pl okres próbny / próbne · it prova · tr deneme · be пробны перыяд ·
uk пробний період · ro perioadă de probă. Keep the tone of the existing translation (du/tu/ty/sen/ты/ти; vous in fr).

## 1. Landing dictionary `i18n/<lang>.json`

Your task file: `i18n/tasks/trial-<lang>.json`.

- `landing_strings`: new keys. Add each to `"strings"` with the key copied byte for byte from `en` and your
  translation as the value. `ru` is the Russian original for context. Same HTML tags, same digits.
- `landing_old`: the keys these replace, with their current translations. Reuse that wording (only the trial and
  beta parts change), then delete these old keys from `"strings"`.
- `ld_faq`: rewrite these items of `"ld"` → `"faq"` (a list of `[question, answer]` pairs, index from 0) from the new
  English text: `"2"` answer, `"4"` answer, `"6"` question and answer.
- `meta_description_en`: the English home page description changed only in its last sentence ("3-day trial, no
  card"). Make the same change in `"meta"` → `"description"` (do not touch other meta fields).

Check: `PYTHONUTF8=1 py -3.12 i18n/tools/check_landing.py <lang>` → missing 0, extra keys 0, bad tags 0, bad digits 0.

## 2. Guide, examples and policy dictionaries `i18n/pages/<lang>-*.json`

For each of your `i18n/pages/todo-<lang>-<chunk>.json` files: translate the listed English strings and add them to
`i18n/pages/<lang>-<chunk>.json` (same rules as `i18n/pages/README-translators.md`: keys byte for byte, same tags,
same digits). The old versions of these strings are already in that file — find them and reuse their wording.
Leave the old keys in place.

Check: `PYTHONUTF8=1 py -3.12 i18n_pages.py check <lang>` → missing 0, rejected 0. Then delete your todo files.

Work from `D:\Claude\kai-landing`. Valid JSON after every write. Keep helper scripts in your own scratchpad
folder. Touch no other files, no git, no page builds.
