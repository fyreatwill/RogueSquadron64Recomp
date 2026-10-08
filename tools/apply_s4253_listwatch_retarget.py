#!/usr/bin/env python3
"""s4253: retarget the s4222 store watch (whatever range it currently carries) to the sample-stream allocator list words
(phys 0x1499B0..0x1499E8) and raise the row cap to 40000, so the writer that leaves head==0/tail!=0 is named by PC. Idempotent."""
import re
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
pat = re.compile(r"sw_p >= 0x[0-9A-Fa-f]+u && sw_p < 0x[0-9A-Fa-f]+u")
import sys
lo, hi = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("1499B0", "1499E8")  # optional: hex phys LO HI
new = f"sw_p >= 0x{lo}u && sw_p < 0x{hi}u"
n = 0
for p in sorted(RF.glob("funcs_*.c")):
    s = p.read_text()
    t = pat.sub(new, s)
    if t != s:
        p.write_text(t)
        n += 1
print("retargeted files:", n)
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
i = t.index("rs64_s4222_store_watch(char")
m = re.compile(r"rows >= \d+u?").search(t, i)
if m and m.group(0) != "rows >= 40000":
    f.write_text(t[:m.start()] + "rows >= 40000" + t[m.end():])
print("ok")
