"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/04/21 00:00:00.000000
Revised: 2026/04/21 15:28:14.002237

Generates media/icon.png and media/icon.ico for flux.

Design: black-and-white pixel grid with a wavy diagonal pattern.
"""

import io
import struct
from pathlib import Path
from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).parent / "media"
OUT_DIR.mkdir(exist_ok=True)

BLACK = (30, 28, 28)
WHITE = (255, 255, 255)

# 10x10 pattern
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
    img  = Image.new("RGBA", (size, size), (*WHITE, 255))
    draw = ImageDraw.Draw(img)
    cell = size / len(PATTERN)
    for r, row in enumerate(PATTERN):
        for c, val in enumerate(row):
            if val:
                x0, y0 = c * cell, r * cell
                draw.rectangle([x0, y0, x0 + cell, y0 + cell], fill=(*BLACK, 255))
    return img


def main():
    icon = make_icon(256)
    icon.save(OUT_DIR / "icon.png")
    print("Saved icon.png")

    ico_sizes = [16, 24, 32, 48, 64, 72, 96, 128, 256]
    png_datas = []
    for s in ico_sizes:
        buf = io.BytesIO()
        make_icon(s).save(buf, format="PNG")
        png_datas.append(buf.getvalue())

    n = len(ico_sizes)
    header = struct.pack("<HHH", 0, 1, n)
    dir_offset = 6 + n * 16
    entries = b""
    offset = dir_offset
    for s, data in zip(ico_sizes, png_datas, strict=True):
        w, h = (s, s) if s < 256 else (0, 0)
        entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (OUT_DIR / "icon.ico").write_bytes(header + entries + b"".join(png_datas))
    print("Saved icon.ico")


if __name__ == "__main__":
    main()
