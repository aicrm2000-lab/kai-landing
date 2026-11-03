# -*- coding: utf-8 -*-
"""Отправить все адреса из sitemap.xml в IndexNow (Bing, Яндекс, Seznam, Naver…), когда сайт уже отдаёт новые страницы.
Запуск: py -3.12 indexnow_submit.py [путь-для-проверки …]   — ждёт до 10 минут, пока каждый путь не ответит 200, потом шлёт."""
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = "aii-crm.com"
KEY = "7242143c1513a5db76fc0bf2934cd6bf"


def live(path: str) -> bool:
    try:
        req = urllib.request.Request(f"https://{HOST}/{path}?cb={int(time.time())}", method="HEAD", headers={"User-Agent": "kai-indexnow-check"})
        return urllib.request.urlopen(req, timeout=20).status == 200
    except Exception:
        return False


def main() -> int:
    waits = [p.lstrip("/") for p in sys.argv[1:]]   # "/en/" и "en/" — одно и то же
    deadline = time.time() + 600
    while waits and time.time() < deadline:
        waits = [p for p in waits if not live(p)]
        if waits:
            time.sleep(20)
    if waits:
        print("not live after 10 minutes:", ", ".join(waits))
        return 1
    urls = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(HERE, "sitemap.xml"), encoding="utf-8").read())
    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    status = urllib.request.urlopen(req, timeout=30).status
    print(f"IndexNow: {len(urls)} URLs, HTTP {status}")
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
