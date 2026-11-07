# -*- coding: utf-8 -*-
"""Настоящие даты правок для sitemap.xml и JSON-LD dateModified: последний коммит файла (один `git log --name-only`),
изменённый или новый в рабочей копии файл — сегодня. До 07.11.2026 у всех 204 URL стояла дата сборки, а Bing такие lastmod
игнорирует и страницы кейсов «менялись» при каждой сборке. Снимок берём ДО пересборки страниц (build_guides.main):
иначе только что сгенерированные файлы выглядят изменёнными и снова получают «сегодня»."""
import datetime as dt
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = dt.date.today().isoformat()
_CACHE: dict | None = None


def lastmods() -> dict:
    """Файл (путь от корня репо, прямые слэши) → YYYY-MM-DD. Кэшируется на процесс."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    dates: dict = {}
    try:
        def run(*a):
            return subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", timeout=60).stdout
        cur = None
        for line in run("log", "--format=%x00%cs", "--name-only").splitlines():
            if line.startswith("\x00"):
                cur = line[1:].strip()
            elif line.strip() and cur:
                dates.setdefault(line.strip(), cur)
        for line in run("status", "--porcelain").splitlines():
            if len(line) > 3:
                dates[line[3:].split(" -> ")[-1].strip().strip('"')] = TODAY
    except Exception:
        pass
    _CACHE = dates
    return dates


def date_of(*files: str) -> str:
    """Дата последней правки любого из файлов-источников (для dateModified сгенерированных страниц)."""
    d = lastmods()
    known = [d[f] for f in files if f in d]   # неизвестные git файлы (нет словаря у языка) не считаем
    return max(known) if known else TODAY


def page_lastmod(url_path: str) -> str:
    """lastmod страницы sitemap по её файлу: «guides/x.html» → тот же файл, «de/» → de/index.html."""
    f = url_path if url_path.endswith(".html") else url_path + "index.html"
    return lastmods().get(f, TODAY)
