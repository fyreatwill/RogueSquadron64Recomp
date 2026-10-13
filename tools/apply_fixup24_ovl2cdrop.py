#!/usr/bin/env python3
"""Apply only fixup 24 (ovl2c drop route) to an already-fixed factor5_ucode_recompiled.c.

The full fixup_factor5_ucode.py is not re-runnable on a fixed file (exact-count anchors), so this
extracts the idempotent fixup-24 block from it and runs it standalone. Usage: apply_fixup24_ovl2cdrop.py <file.c>
"""
import sys
from pathlib import Path

src = Path(__file__).with_name("fixup_factor5_ucode.py").read_text()
blk = src[src.index("OVL2C_DROP_MARKER = "):src.index("# Make sure <cstdio>")]
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
exec(blk)
path.write_text(text, encoding="utf-8")
print("ovl2cdrop present:", "fixup: ovl2cdrop" in text)
