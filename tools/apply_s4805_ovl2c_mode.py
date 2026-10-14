#!/usr/bin/env python3
"""s4805: make the overlay-0x2C route switchable (ROGUESQ_OVL2C_MODE).

ORIGIN: the s4751 stopgap `ROGUESQ_OVL2C_DROP` (fixup 24) sits AFTER the s4756
splice route (fixup 6r) at the same `0x153 == 0x2C` test, so since s4773 the
drop branch was dead code and every "DROP=0 vs DROP=1" A/B (s4787/s4788/s4802/
s4804) compared the splice with itself. This replaces the two branches with one
switch: MODE 0 = resident splice (default), 1 = drop (cull path, the old
stopgap; legacy ROGUESQ_OVL2C_DROP=1 maps here), 2 = neither (original
fall-through to L_1DB0, the unrouted runaway-reproduction control).

The same BLOCK text is emitted by fixup 6r in tools/fixup_factor5_ucode.py
(imported from here is not possible, so keep the two in sync).

Usage: apply_s4805_ovl2c_mode.py <factor5_ucode_recompiled.c>
"""
import re, sys
from pathlib import Path

BLOCK = ("            if (RSP_MEM_BU(0X153, 0) == 0x2C) {"
         " static int rs64_2c_mode = -1;"
         " if (rs64_2c_mode < 0) { const char *m = std::getenv(\"ROGUESQ_OVL2C_MODE\");"
         " const char *d = std::getenv(\"ROGUESQ_OVL2C_DROP\");"
         " rs64_2c_mode = (m && *m) ? (*m - '0') : ((d && *d == '1') ? 1 : 0); }"
         " if (rs64_2c_mode == 0) { rs64_e9prov_ovl_route(0x2C, 0x1DB0); goto OVL2C_1DB0; }"
         " if (rs64_2c_mode == 1) { rs64_e9prov_ovl_route(0x2C, 0x1DB0);"
         " r17 = RSP_ADD32(r17, 0X10); goto L_10D8; } }  ")
OLD_SPLICE = ("            if (RSP_MEM_BU(0X153, 0) == 0x2C) {"
              " rs64_e9prov_ovl_route(0x2C, 0x1DB0); goto OVL2C_1DB0; }  ")
OLD_DROP_RE = re.compile(
    r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x2C\) \{ static int rs64_2c_drop = -1;.*?"
    r"goto L_10D8; \} \}  /\* fixup: ovl2cdrop \*/\n", re.S)

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "rs64_2c_mode" in t:
    print("already applied")
    sys.exit(0)
assert t.count(OLD_SPLICE + "/* fixup: ovl2csplice */") == 1
t = t.replace(OLD_SPLICE, BLOCK)
t, n = OLD_DROP_RE.subn("", t)
assert n == 1, n
p.write_text(t, encoding="utf-8")
print("applied")
