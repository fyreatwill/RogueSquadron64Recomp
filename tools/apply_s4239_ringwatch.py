#!/usr/bin/env python3
"""s4239: retarget the s4222 guest store watch (currently the s4230 allocator-list range 0x1499B0..0x1499E8) to the
AI output ring (phys 0x166450..0x169450, 12 x 0x300) and aggregate rows per store PC in rs64_s4222_store_watch
(first sight + every 500th), to name the non-ucode writer that turns ucode output (rms 2-6k) into the AI-consumed
buffer (rms ~19k). Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLDR = "sw_p >= 0x1499B0u && sw_p < 0x1499E8u"
NEWR = "sw_p >= 0x166450u && sw_p < 0x169450u"
n = 0
for p in sorted(RF.glob("funcs_*.c")):
    s = p.read_text()
    if OLDR in s:
        p.write_text(s.replace(OLDR, NEWR)); n += 1
print("retargeted files:", n)
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
if "s4239 ring" not in t:
    a = "    uint32_t li = (addr >> 2) & 63u;\n"
    assert t.count(a) == 1
    b = '''    { // s4239 ring: aggregate per store PC
        static struct { uint32_t pc; unsigned long n; } pcs[64];
        static int npc = 0;
        int k = 0; while (k < npc && pcs[k].pc != pc) k++;
        if (k == npc && npc < 64) { pcs[npc].pc = pc; pcs[npc].n = 0; npc++; }
        if (k >= 64) return;
        unsigned long c = ++pcs[k].n;
        if (c == 1 || (c % 500) == 0)
            std::fprintf(stderr, "[s4239-ringS] w=%u pc=%08X %c addr=%08X val=%08X cnt=%lu\\n", rs64_vi_committed_width(), pc, width, addr, value, c);
        return;
    }
'''
    f.write_text(t.replace(a, b + a))
print("ok")
