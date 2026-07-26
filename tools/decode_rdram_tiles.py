#!/usr/bin/env python3
"""Decode the contiguous 0x65xxxx RDRAM blocks the hangar compositor loads.

Two competing readings of the same bytes:
  (a) each 4096-byte block is one 64x32 RGBA16 tile (what the LOADBLOCK claims:
      words=512, dxt=128 => 16 words = 64 texels per row);
  (b) the whole region is one linear 512-wide RGBA16 image (what it would be if
      this is a rendered/decompressed full-width picture the game tiles out of).

Whichever produces a coherent picture tells us what the source really is.
RDRAM in this recomp is byte-swizzled, so every byte index is read as i^3.
"""
import glob
import os
import struct
import sys

from PIL import Image

SCRATCH = "/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build"
OUT = "/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s17_decode"


def rgba16(hi, lo):
    v = (hi << 8) | lo
    r = ((v >> 11) & 0x1F) * 255 // 31
    g = ((v >> 6) & 0x1F) * 255 // 31
    b = ((v >> 1) & 0x1F) * 255 // 31
    return (r, g, b)


def unswizzle(data):
    """Undo the ^3 byte order so multi-byte reads see hardware order."""
    out = bytearray(len(data))
    n = len(data) & ~3
    for i in range(n):
        out[i] = data[i ^ 3]
    return bytes(out)


def decode(data, width, swizzled=True):
    if swizzled:
        data = unswizzle(data)
    px = len(data) // 2
    height = px // width
    im = Image.new("RGB", (width, height))
    put = im.putpixel
    for i in range(width * height):
        put((i % width, i // width), rgba16(data[i * 2], data[i * 2 + 1]))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SCRATCH, "rdram_load_65*_f0.bin")) +
                   glob.glob(os.path.join(SCRATCH, "rdram_load_6[67]*_f0.bin")))
    if not files:
        print("no dumps")
        return 1
    print(f"{len(files)} blocks")

    blob = b"".join(open(f, "rb").read() for f in files)
    print(f"total {len(blob)} bytes")

    # (a) per-block 64x32 tiles, laid out in a grid for inspection
    cols = 8
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 64, rows * 32))
    for i, f in enumerate(files):
        t = decode(open(f, "rb").read(), 64)
        sheet.paste(t, ((i % cols) * 64, (i // cols) * 32))
    sheet.resize((cols * 64 * 3, rows * 32 * 3), Image.NEAREST).save(
        os.path.join(OUT, "a_tiles_64x32.png"))

    # (b) the region as one linear image, at the widths worth trying
    for w in (512, 320, 256, 128, 64):
        im = decode(blob, w)
        if im.height > 4000:
            im = im.crop((0, 0, w, 4000))
        im.save(os.path.join(OUT, f"b_linear_{w}.png"))

    # control: same bytes with no unswizzle, in case the dump is already in order
    decode(blob[:4096 * 8], 64, swizzled=False).save(
        os.path.join(OUT, "c_noswizzle_64.png"))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
