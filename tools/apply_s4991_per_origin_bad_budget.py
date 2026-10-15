#!/usr/bin/env python3
"""s4991: reset the diagnostic bad-row budget at each committed VI origin.

Diagnostic only. This preserves the caller-boundary values and does not
rewrite, reject, or guard any game value.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
p = root / "funcs_24.c"
s = p.read_text()
marker = "PATCH: s4991 per-origin bad budget"
if marker in s:
    print("s4991 already applied")
    raise SystemExit(0)

var_anchor = "static int rs64_s4540_bad_rows = 0;\n"
if s.count(var_anchor) != 1:
    raise SystemExit(f"bad-row variable anchor count={s.count(var_anchor)}")
s = s.replace(
    var_anchor,
    var_anchor
    + "static uint32_t rs64_s4540_bad_origin = 0;\n"
    + "static int rs64_s4540_bad_origin_valid = 0;\n",
    1,
)

call_anchor = "    if (!rs64_s4540_enabled()) return;\n"
if s.count(call_anchor) != 1:
    raise SystemExit(f"enabled anchor count={s.count(call_anchor)}")
s = s.replace(
    call_anchor,
    call_anchor
    + "    {\n"
    + "        const uint32_t origin = rs64_vi_committed_origin();\n"
    + "        if (!rs64_s4540_bad_origin_valid || origin != rs64_s4540_bad_origin) {\n"
    + "            rs64_s4540_bad_origin = origin;\n"
    + "            rs64_s4540_bad_origin_valid = 1;\n"
    + "            rs64_s4540_bad_rows = 0;\n"
    + "        }\n"
    + "    } /* PATCH: s4991 per-origin bad budget */\n",
    1,
)
p.write_text(s)
print("s4991 per-origin bad budget applied")
