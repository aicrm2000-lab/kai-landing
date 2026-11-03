# -*- coding: utf-8 -*-
"""Проверка словарей i18n/<lang>.json против i18n/source.json: все ключи, теги и цифры совпадают, meta/ld/ui полные,
слова частиц ≤ 8 символов, нет пустых переводов и переводов, равных английскому (кроме коротких/брендовых)."""
import io, json, os, re, sys

ROOT = r"D:\Claude\kai-landing"
src = json.load(io.open(os.path.join(ROOT, "i18n", "source.json"), encoding="utf-8"))
keys = [i["en"] for i in src["items"]]
codes = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "i18n")) if f.endswith(".json") and f != "source.json")
tags = lambda s: re.findall(r"<[^>]+>", s)
digits = lambda s: sorted(re.findall(r"\d+", s))
ok_all = True
for code in codes:
    p = os.path.join(ROOT, "i18n", f"{code}.json")
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"{code}: JSON ERROR {e}"); ok_all = False; continue
    S = d.get("strings", {})
    missing = [k for k in keys if k not in S]
    empty = [k for k in keys if k in S and not str(S[k]).strip()]
    bad_tags = [k for k in keys if k in S and tags(S[k]) != tags(k)]
    bad_digits = [k for k in keys if k in S and digits(S[k]) != digits(k)]
    same = [k for k in keys if k in S and S[k] == k and len(k) > 12 and not re.match(r"^[A-Z0-9 /×·._-]+$", k)]
    extra = [k for k in S if k not in set(keys)]
    problems = []
    for sec, need in (("meta", ["title", "description", "og_title", "og_description", "keywords"]),
                      ("ui", ["lang_name", "lang_label", "kai_note", "words", "words_ny", "theme_hw", "theme_ny", "turn_on", "turn_off", "actions_word"])):
        for k in need:
            if not d.get(sec, {}).get(k):
                problems.append(f"{sec}.{k} missing")
    ld = d.get("ld", {})
    if len(ld.get("featureList", [])) != 8: problems.append("ld.featureList != 8")
    if len(ld.get("faq", [])) != 7 or any(len(x) != 2 for x in ld.get("faq", [])): problems.append("ld.faq != 7 pairs")
    if not ld.get("description"): problems.append("ld.description missing")
    for wk in ("words", "words_ny"):
        for w in d.get("ui", {}).get(wk, []):
            if w != "{year}" and (len(w) > 8 or w != w.upper()):
                problems.append(f"ui.{wk}: '{w}' (>8 chars or not uppercase)")
    if len(d.get("ui", {}).get("words_ny", [])) < 8: problems.append("ui.words_ny < 8 words")
    long_titles = [k for k in keys if k in S and len(k) <= 20 and len(S[k]) > max(28, int(len(k) * 1.8))]
    print(f"{code}: strings {len(S)} | missing {len(missing)} | empty {len(empty)} | bad tags {len(bad_tags)} | bad digits {len(bad_digits)} | "
          f"same as EN {len(same)} | extra keys {len(extra)} | long short-labels {len(long_titles)} | other: {problems or 'ok'}")
    for lbl, arr in (("missing", missing), ("empty", empty), ("bad tags", bad_tags), ("bad digits", bad_digits), ("same", same), ("long", long_titles)):
        for k in arr[:4]:
            print(f"   {lbl}: {k[:70]!r} -> {str(S.get(k, ''))[:70]!r}")
    if missing or empty or bad_tags or bad_digits or problems:
        ok_all = False
print("ALL OK" if ok_all else "ISSUES")
