# -*- coding: utf-8 -*-
"""Файлы значка сайта из знака Kai (тот же рисунок, что был вшит data:-адресом): Google и Bing показывают значок
в выдаче только по отдельному файлу на сайте, data:-адреса они не берут.

Пишет: favicon.svg, favicon.ico (16/32/48), favicon-48.png, favicon-96.png, apple-touch-icon.png (180),
icon-192.png, icon-512.png (он же логотип для разметки Organization).
Запуск: py -3.12 make_icons.py"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
BG, ARC, DOT = (11, 10, 20, 255), (124, 92, 255, 255), (167, 139, 250, 255)
SVG = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='#0B0A14'/>"
       "<path d='M16 6.5a9.5 9.5 0 1 0 9.5 9.5' stroke='#7C5CFF' stroke-width='4' stroke-linecap='round' fill='none'/>"
       "<circle cx='23.4' cy='8.6' r='2.6' fill='#A78BFA'/></svg>\n")


def draw(size: int, rounded: bool = True) -> Image.Image:
    """Рисуем в 8× и уменьшаем — сглаженные края. Координаты как в SVG (viewBox 32)."""
    k = size * 8 / 32
    big = Image.new("RGBA", (size * 8, size * 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    if rounded:
        d.rounded_rectangle([0, 0, size * 8 - 1, size * 8 - 1], radius=int(8 * k), fill=BG)
    else:
        d.rectangle([0, 0, size * 8 - 1, size * 8 - 1], fill=BG)
    cx, cy, r, w = 16 * k, 16 * k, 9.5 * k, 4 * k
    # дуга 270°: от правой точки по часовой через низ и левую сторону к верхней (как path в SVG)
    d.arc([cx - r - w / 2, cy - r - w / 2, cx + r + w / 2, cy + r + w / 2], start=0, end=270, fill=ARC, width=int(round(w)))
    for x, y in ((cx + r, cy), (cx, cy - r)):            # круглые концы
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=ARC)
    dx, dy, dr = 23.4 * k, 8.6 * k, 2.6 * k
    d.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=DOT)
    return big.resize((size, size), Image.LANCZOS)


def main() -> None:
    open(os.path.join(HERE, "favicon.svg"), "w", encoding="utf-8", newline="\n").write(SVG)
    draw(48).save(os.path.join(HERE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    for name, size, rounded in (("favicon-48.png", 48, True), ("favicon-96.png", 96, True),
                                ("apple-touch-icon.png", 180, False),   # iOS скругляет сам
                                ("icon-192.png", 192, True), ("icon-512.png", 512, True)):
        draw(size, rounded).save(os.path.join(HERE, name), optimize=True)
    print("icons written")


if __name__ == "__main__":
    main()
