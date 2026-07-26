#!/usr/bin/env python3
"""Decode a set of 4 KB RDRAM texture dumps under competing format readings.

Session 17 established the method: when a texture population renders wrong, the
fastest way to find out whether the *format* the stream claims is real is to
decode the same bytes several ways and see which one produces a coherent
picture. That script hardcoded one population and one reading; this one takes
any dumps written by ROGUESQ_DUMP_TMEM_LOAD and renders each candidate layout
side by side, because a 4096-byte block is 32x32 as RGBA32 and 64x32 as RGBA16
and nothing about the byte count alone distinguishes them.

RDRAM in this recomp is byte-swizzled, so every byte index is read as i^3.

Usage: decode_block_formats.py <out-prefix> <dump.bin...>
"""
import os
import sys

from PIL import Image


def unswizzle(data):
    out = bytearray(len(data))
    n = len(data) & ~3
    for i in range(n):
        out[i] = data[i ^ 3]
    return bytes(out)


def rgba16_px(v):
    r = ((v >> 11) & 0x1F) * 255 // 31
    g = ((v >> 6) & 0x1F) * 255 // 31
    b = ((v >> 1) & 0x1F) * 255 // 31
    return (r, g, b)


def as_rgba16(data, w, h):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            o = (y * w + x) * 2
            if o + 1 >= len(data):
                continue
            px[x, y] = rgba16_px((data[o] << 8) | data[o + 1])
    return im


def as_rgba32(data, w, h):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            o = (y * w + x) * 4
            if o + 3 >= len(data):
                continue
            px[x, y] = (data[o], data[o + 1], data[o + 2])
    return im


def as_i8(data, w, h):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            o = y * w + x
            if o >= len(data):
                continue
            v = data[o]
            px[x, y] = (v, v, v)
    return im


# name -> (decoder, width, height) for a 4096-byte block
READINGS = {
    "rgba32_32x32": (as_rgba32, 32, 32),
    "rgba16_64x32": (as_rgba16, 64, 32),
    "rgba16_32x64": (as_rgba16, 32, 64),
    "i8_64x64": (as_i8, 64, 64),
}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    prefix = argv[1]
    files = sorted(argv[2:])
    blocks = []
    for f in files:
        with open(f, "rb") as fh:
            blocks.append(unswizzle(fh.read()))
    print(f"{len(blocks)} blocks of {len(blocks[0])} bytes")

    cols = 6
    for name, (dec, w, h) in READINGS.items():
        rows = (len(blocks) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
        for i, b in enumerate(blocks):
            sheet.paste(dec(b, w, h), ((i % cols) * w, (i // cols) * h))
        # Upscale so a thumbnail is legible without hiding structure.
        sheet = sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST)
        out = f"{prefix}_{name}.png"
        sheet.save(out)
        print(f"  {out}  {sheet.size[0]}x{sheet.size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
