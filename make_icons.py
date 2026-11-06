# -*- coding: utf-8 -*-
"""Файлы значка сайта из знака Kai: Google и Bing показывают значок в выдаче только по отдельному файлу на сайте,
data:-адреса они не берут.

06.11.2026, вариант 1 из четырёх (Тихон: «кружок и в нём чуть меньше наш лого»): чёрный круг #0B0B0B
с прозрачными углами, в нём знак чернилами #F4F4F2, уменьшенный до 0.68 (внешний край кольца ≈ 10.3 из 16).
Пропорции знака — как у ч/б знака в marketing/brand/make_bw_logo_anim.py (кольцо 6°→270°, толщина 0.46 радиуса,
точка в разрыве под 311.6°).
apple-touch-icon.png — сплошной квадрат без прозрачности: iOS сама скругляет углы, а прозрачные заливает чёрным.
До 06.11 значок был квадратом с кольцом во всю ширину — Тихону не понравилось во вкладке.

Пишет: favicon.svg, favicon.ico (16/32/48), favicon-48.png, favicon-96.png, apple-touch-icon.png (180),
icon-192.png, icon-512.png (он же логотип для разметки Organization).
Запуск: py -3.12 make_icons.py"""
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
BG, INK = (11, 11, 11, 255), (244, 244, 242, 255)
S = 0.68                                  # знак относительно круга («чуть меньше»)
# координаты в viewBox 32: центр 16; у полноразмерного знака средний радиус кольца 12.3, толщина 5.6
C, R, W = 16.0, 12.3 * S, 5.6 * S
A0, A1 = 6.0, 270.0                       # дуга по часовой от «3 часов»; разрыв — справа сверху
DOT_ANG, DOT_DIST, DOT_R = 311.6, 12.3 * S, 3.5 * S


def _xy(ang: float, dist: float) -> tuple[float, float]:
    a = math.radians(ang)
    return C + dist * math.cos(a), C + dist * math.sin(a)


def svg() -> str:
    x0, y0 = _xy(A0, R)
    x1, y1 = _xy(A1, R)
    dx, dy = _xy(DOT_ANG, DOT_DIST)
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='16' fill='#0B0B0B'/>"
            f"<path d='M{x0:.2f} {y0:.2f}A{R:.2f} {R:.2f} 0 1 1 {x1:.2f} {y1:.2f}' stroke='#F4F4F2' "
            f"stroke-width='{W:.2f}' stroke-linecap='round' fill='none'/>"
            f"<circle cx='{dx:.2f}' cy='{dy:.2f}' r='{DOT_R:.2f}' fill='#F4F4F2'/></svg>\n")


def draw(size: int, square: bool = False) -> Image.Image:
    """Рисуем в 8× и уменьшаем — сглаженные края. Координаты как в SVG (viewBox 32).
    square=True — фон на весь квадрат (для apple-touch-icon), иначе круг с прозрачными углами."""
    k = size * 8 / 32
    big = Image.new("RGBA", (size * 8, size * 8), BG if square else (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    if not square:
        d.ellipse([0, 0, size * 8 - 1, size * 8 - 1], fill=BG)
    c, r, w = C * k, R * k, W * k
    d.arc([c - r - w / 2, c - r - w / 2, c + r + w / 2, c + r + w / 2], start=A0, end=A1, fill=INK, width=int(round(w)))
    for ang in (A0, A1):                                  # круглые концы
        x, y = _xy(ang, R)
        x, y = x * k, y * k
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=INK)
    dx, dy = _xy(DOT_ANG, DOT_DIST)
    dx, dy, dr = dx * k, dy * k, DOT_R * k
    d.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=INK)
    return big.resize((size, size), Image.LANCZOS)


def main() -> None:
    open(os.path.join(HERE, "favicon.svg"), "w", encoding="utf-8", newline="\n").write(svg())
    draw(48).save(os.path.join(HERE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    for name, size, square in (("favicon-48.png", 48, False), ("favicon-96.png", 96, False),
                               ("apple-touch-icon.png", 180, True),
                               ("icon-192.png", 192, False), ("icon-512.png", 512, False)):
        draw(size, square).save(os.path.join(HERE, name), optimize=True)
    print("icons written")


if __name__ == "__main__":
    main()
