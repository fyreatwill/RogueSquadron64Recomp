#!/usr/bin/env python3
"""Summarise a capture burst so a run can be judged without opening 100 PNGs.

Per frame: dominant colour and its share, distinct-colour count, and a
"content" verdict. A frame that is one flat colour (black clear, white clear,
the desktop) is not content no matter how bright it is; a frame with real
geometry has thousands of distinct colours and no single colour dominating.

Usage: frames.py <dir-or-files...> [--top N]
"""
import sys
import os
from collections import Counter

from PIL import Image

# Downsample before counting: exact pixel identity is not the question, "is
# there structure here" is, and full-res counting on 100 frames is slow.
SAMPLE = 256


def stats(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    im = im.resize((min(SAMPLE, w), min(SAMPLE, h)), Image.NEAREST)
    px = list(im.getdata())
    total = len(px)
    counts = Counter(px)
    dom, domn = counts.most_common(1)[0]
    distinct = len(counts)
    domshare = domn / total

    # Thresholds chosen against known-good captures: the flat clears in this
    # game land above 0.97 dominant share with a handful of distinct colours,
    # real frames sit near 0.3-0.7 with thousands.
    content = (distinct > 200) and (domshare < 0.95)
    return dict(path=path, size=(w, h), dom=dom, domshare=domshare,
                distinct=distinct, content=content)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = []
    for a in args:
        if os.path.isdir(a):
            files += [os.path.join(a, f) for f in sorted(os.listdir(a))
                      if f.lower().endswith(".png")]
        else:
            files.append(a)

    if not files:
        print("no png files")
        return 1

    ncontent = 0
    for f in files:
        try:
            s = stats(f)
        except Exception as exc:                      # unreadable/partial capture
            print(f"{os.path.basename(f):28s} ERROR {exc}")
            continue
        ncontent += bool(s["content"])
        flag = "CONTENT" if s["content"] else "  flat "
        print(f"{os.path.basename(f):28s} {s['size'][0]}x{s['size'][1]:<5d} "
              f"{flag} dom=#{s['dom'][0]:02x}{s['dom'][1]:02x}{s['dom'][2]:02x} "
              f"share={s['domshare']:.3f} distinct={s['distinct']}")

    print(f"\n{ncontent}/{len(files)} frames have content")
    return 0


if __name__ == "__main__":
    sys.exit(main())
