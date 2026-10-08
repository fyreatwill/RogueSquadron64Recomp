#!/usr/bin/env python3
"""s4230: retarget the s4222 store watch from the volume bytes (0x130B5C..64) to the sample-stream allocator list
words (pool 0x801499CC, tail 0x801499B4, head 0x801499E4; phys 0x1499B0..0x1499E8) to name the writer that leaves
head==0 with tail!=0 (fillSampleStreamRange+8136 null deref at lw $a0,0($v1) 0x8008FD60). Row cap 60 -> 6000. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLDR = "sw_p >= 0x130B5Cu && sw_p < 0x130B64u"
NEWR = "sw_p >= 0x1499B0u && sw_p < 0x1499E8u"
n = 0
for p in sorted(RF.glob("funcs_*.c")):
    s = p.read_text()
    if OLDR in s:
        p.write_text(s.replace(OLDR, NEWR)); n += 1
print("retargeted files:", n)
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
if "rows >= 6000" not in t:
    a = "if (rows >= 60) return;"
    assert t.count(a) == 1
    f.write_text(t.replace(a, "if (rows >= 6000) return;"))
