#!/usr/bin/env python3
"""Визуальная сверка вёрстки с эталоном из Figma (вторичная проверка).

Usage:
    python3 pixel_diff.py <figma_ref.png> <render.png> [--out diff.png] [--threshold 3.0]

Выводит % расходящихся пикселей, heatmap и разбивку по зонам 4x4,
чтобы было видно, ГДЕ расхождение. Помни: антиалиасинг и рендер шрифтов
дают фоновый шум 1-3% — значения, совпадающие со спекой, не трогать.

Exit code: 0 если diff <= threshold (%), иначе 1.
Зависимость: Pillow (pip install pillow).
"""

from __future__ import annotations

import argparse
import sys

try:
    from PIL import Image, ImageChops
except ImportError:
    sys.exit("Нужен Pillow: pip install pillow")

# Разница каналов ниже этого (0-255) считается шумом антиалиасинга.
NOISE = 16
GRID = 4


def max_channel_diff(a: Image.Image, b: Image.Image) -> Image.Image:
    """Максимум расхождения по RGB-каналам (усреднение прячет цветовые промахи)."""
    d = ImageChops.difference(a, b)
    r, g, bl = d.split()
    return ImageChops.lighter(ImageChops.lighter(r, g), bl)


def bad_ratio(gray: Image.Image) -> float:
    """Доля пикселей ярче NOISE — через гистограмму, без попиксельного цикла."""
    hist = gray.histogram()
    total = gray.size[0] * gray.size[1]
    return sum(hist[NOISE + 1:]) / total if total else 0.0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("reference", help="Эталонный скриншот из Figma")
    p.add_argument("render", help="Скриншот твоей вёрстки")
    p.add_argument("--out", default="_diff.png", help="Куда сохранить heatmap")
    p.add_argument("--threshold", type=float, default=3.0, help="Порог diff в %%")
    args = p.parse_args()

    ref = Image.open(args.reference).convert("RGB")
    ren = Image.open(args.render).convert("RGB")

    if ref.size != ren.size:
        rw, rh = ref.size
        nw, nh = ren.size
        if abs(rw / nw - rh / nh) < 0.01:
            print(f"ℹ️  Разный масштаб (эталон {ref.size}, рендер {ren.size}), "
                  f"пропорции совпадают — привожу (retina 2x?).")
        else:
            print(f"⚠️  ПРОПОРЦИИ не совпадают: эталон {ref.size}, рендер {ren.size}.")
            print("    Это расхождение вёрстки: проверь вьюпорт и габариты фрейма из metadata.")
        ren = ren.resize(ref.size, Image.LANCZOS)

    gray = max_channel_diff(ref, ren)
    pct = 100.0 * bad_ratio(gray)

    # Heatmap: расхождения красным поверх приглушённого эталона
    heat = ref.copy().point(lambda v: v // 3)
    mask = gray.point(lambda v: 255 if v > NOISE else 0)
    heat.paste(Image.new("RGB", ref.size, (255, 40, 40)), mask=mask)
    heat.save(args.out)

    # Локализация: зоны GRID x GRID, показываем горячие
    w, h = gray.size
    cells = []
    for gy in range(GRID):
        for gx in range(GRID):
            box = (w * gx // GRID, h * gy // GRID, w * (gx + 1) // GRID, h * (gy + 1) // GRID)
            cell_pct = 100.0 * bad_ratio(gray.crop(box))
            cells.append((cell_pct, gx, gy, box))

    print(f"Diff: {pct:.2f}% пикселей (порог шума {NOISE}/255)")
    print(f"Heatmap: {args.out}")
    hot = [c for c in sorted(cells, reverse=True) if c[0] > max(2.0, pct)][:5]
    if hot:
        print("Горячие зоны (строка/колонка от левого верха, % расхождения):")
        for cell_pct, gx, gy, box in hot:
            print(f"  строка {gy + 1}/{GRID}, колонка {gx + 1}/{GRID}: "
                  f"{cell_pct:.1f}%  px({box[0]},{box[1]})-({box[2]},{box[3]})")

    if pct <= args.threshold:
        print(f"✅ В пределах порога {args.threshold}% (остаток — шум рендера шрифтов)")
        return 0
    print(f"❌ Выше порога {args.threshold}% — ищи СТРУКТУРНЫЕ промахи в горячих зонах.")
    print("   Значения, совпадающие со спекой, не менять ради снижения diff.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
