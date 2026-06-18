#!/usr/bin/env python3
"""Pixelate generated fighter portraits to match the shipped roster style.

Shipped portraits measure ~160px effective resolution, a few hundred colors,
256x256 output. Pipeline: center-crop square -> BOX downscale -> saturation
bump -> NEAREST upscale to 256. Optional MEDIANCUT quantize.
"""
import sys
from PIL import Image, ImageEnhance


def pixelate(src, dst, down=160, sat=1.25, colors=0, out=256):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    im = im.resize((down, down), Image.BOX)
    im = ImageEnhance.Color(im).enhance(sat)
    if colors:
        im = im.quantize(colors=colors, method=Image.MEDIANCUT).convert("RGB")
    im = im.resize((out, out), Image.NEAREST)
    im.save(dst)
    n = len(im.getcolors(999999))
    print(f"{dst}  colors={n}")


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    down = int(sys.argv[3]) if len(sys.argv) > 3 else 160
    colors = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    pixelate(src, dst, down=down, colors=colors)
