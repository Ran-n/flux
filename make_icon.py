"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/04/21 00:00:00.000000
Revised: 2026/04/21 14:28:20.970259

Generates media/icon.png and media/icon.ico for flux.

Design: black-and-white pixel grid with a wavy diagonal pattern.
"""

from pathlib import Path
from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).parent / "media"
OUT_DIR.mkdir(exist_ok=True)

SIZE  = 256
BLACK = (30, 28, 28)
WHITE = (255, 255, 255)

# 10x10 — pixel art, loosely QR-inspired but not obviously a QR code
PATTERN = [
    [1,1,0,0,0,0,1,1,0,0],
    [1,1,0,1,0,0,0,0,0,1],
    [0,0,0,1,1,0,1,0,0,0],
    [0,1,0,0,1,0,0,0,1,1],
    [0,1,1,0,0,0,0,1,1,0],
    [0,0,1,0,0,1,1,0,0,0],
    [1,0,0,0,1,1,0,0,1,0],
    [1,0,0,1,0,0,0,1,1,0],
    [0,0,1,0,0,0,1,1,0,1],
    [0,1,1,0,0,1,1,0,0,1],
]


def make_icon(size: int) -> Image.Image:
    img  = Image.new("RGB", (size, size), WHITE)
    draw = ImageDraw.Draw(img)
    cell = size / len(PATTERN)
    for r, row in enumerate(PATTERN):
        for c, val in enumerate(row):
            if val:
                x0, y0 = c * cell, r * cell
                draw.rectangle([x0, y0, x0 + cell, y0 + cell], fill=BLACK)
    return img


def main():
    icon = make_icon(SIZE)
    icon.save(OUT_DIR / "icon.png")
    print("Saved icon.png")

    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    frames = [make_icon(s) for s in ico_sizes]
    frames[0].save(
        OUT_DIR / "icon.ico",
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=frames[1:],
    )
    print("Saved icon.ico")


if __name__ == "__main__":
    main()
