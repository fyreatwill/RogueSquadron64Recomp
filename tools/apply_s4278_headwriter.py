#!/usr/bin/env python3
"""s4278: name the writer that zeroes the sample-stream allocator list (head 0x801499E4 / tail 0x801499B4 / pool 0x801499CC)
between [s4234-ENTRY] n=9506 and n=9507. Applies s4222 storewatch + s4230 listwatch retarget (idempotent), then gates the
watch row on global rs64_s4234_g >= 9400 (set by the entry probe) so the 6000-row budget is spent in the crash window.
Also logs ENTRY rows for n>=9500. Needs ROGUESQ_LOG_S4222=1. Idempotent."""
import subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
for t in ("apply_s4222_storewatch.py", "apply_s4234_entryprobe.py"):
    subprocess.check_call([sys.executable, str(R / "tools" / t)])
# live watch range is the s4234-era heap window 0x1F9000..0x1FC000; retarget to the list struct words
n = 0
for q in sorted(RF.glob("funcs_*.c")):
    c = q.read_text()
    if "sw_p >= 0x1F9000u && sw_p < 0x1FC000u" in c:
        q.write_text(c.replace("sw_p >= 0x1F9000u && sw_p < 0x1FC000u", "sw_p >= 0x1499B0u && sw_p < 0x1499E8u")); n += 1
print("retargeted", n)
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
if "rs64_s4234_g" not in t:
    a = 'extern "C" void rs64_s4222_store_watch('
    assert t.count(a) == 1
    t = t.replace(a, 'extern "C" volatile unsigned rs64_s4234_g = 0;\n' + a, 1)
    b = "    if (!rs64_s4222_on()) return;\n    static int rows = 0;"
    assert t.count(b) == 1
    t = t.replace(b, "    if (!rs64_s4222_on() || rs64_s4234_g < 9400u) return;\n    static int rows = 0;", 1)
    f.write_text(t)
p = RF / "funcs_24.c"
s = p.read_text()
if "rs64_s4234_g" not in s:
    a = "++s4234_n; "
    assert s.count(a) == 1
    s = s.replace(a, a + "rs64_s4234_g = s4234_n; ", 1)
    s = s.replace("s4234_n <= 30 ||", "s4234_n <= 30 || s4234_n >= 9500 ||", 1)
    s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\nextern volatile unsigned rs64_s4234_g;\n', 1)
    p.write_text(s)
print("ok")
