# -*- coding: utf-8 -*-
"""Файлы значка сайта из знака Kai: Google и Bing показывают значок в выдаче только по отдельному файлу на сайте,
data:-адреса они не берут.

06.11.2026 (Тихон: «значок во всю ширину и чёрно-белый»): кольцо занимает весь квадрат, краски — только чернила
#F4F4F2 на почти чёрном #0B0B0B; пропорции те же, что у ч/б знака в marketing/brand/make_bw_logo_anim.py
(кольцо 6°→270°, толщина 0.46 радиуса, точка в разрыве под 311.6°). В выдаче Google значок обрезается в круг —
скруглённые углы не нужны, фон доходит до краёв.

Пишет: favicon.svg, favicon.ico (16/32/48), favicon-48.png, favicon-96.png, apple-touch-icon.png (180),
icon-192.png, icon-512.png (он же логотип для разметки Organization).
Запуск: py -3.12 make_icons.py"""
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
BG, INK = (11, 11, 11, 255), (244, 244, 242, 255)
# координаты в viewBox 32: центр 16, средний радиус кольца 12.3, толщина 5.6 → внешний край 15.1 (почти до рамки)
C, R, W = 16.0, 12.3, 5.6
A0, A1 = 6.0, 270.0                       # дуга по часовой от «3 часов»; разрыв — справа сверху
DOT_ANG, DOT_DIST, DOT_R = 311.6, 12.3, 3.5


def _xy(ang: float, dist: float) -> tuple[float, float]:
    a = math.radians(ang)
    return C + dist * math.cos(a), C + dist * math.sin(a)


def svg() -> str:
    x0, y0 = _xy(A0, R)
    x1, y1 = _xy(A1, R)
    dx, dy = _xy(DOT_ANG, DOT_DIST)
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' fill='#0B0B0B'/>"
            f"<path d='M{x0:.2f} {y0:.2f}A{R} {R} 0 1 1 {x1:.2f} {y1:.2f}' stroke='#F4F4F2' stroke-width='{W}' "
            "stroke-linecap='round' fill='none'/>"
            f"<circle cx='{dx:.2f}' cy='{dy:.2f}' r='{DOT_R}' fill='#F4F4F2'/></svg>\n")


def draw(size: int) -> Image.Image:
    """Рисуем в 8× и уменьшаем — сглаженные края. Координаты как в SVG (viewBox 32)."""
    k = size * 8 / 32
    big = Image.new("RGBA", (size * 8, size * 8), BG)
    d = ImageDraw.Draw(big)
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
    for name, size in (("favicon-48.png", 48), ("favicon-96.png", 96), ("apple-touch-icon.png", 180),
                       ("icon-192.png", 192), ("icon-512.png", 512)):
        draw(size).save(os.path.join(HERE, name), optimize=True)
    print("icons written")


if __name__ == "__main__":
    main()
