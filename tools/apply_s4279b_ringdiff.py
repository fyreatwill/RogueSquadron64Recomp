#!/usr/bin/env python3
"""s4279b: on top of apply_s4279_nodeinvariant.py. Ring of the last 96 node-region stores (pc/addr/ENTRY n) plus a
per-ENTRY shadow of the whole node region; at the FIRST list-invariant violation dump every changed word since the
previous ENTRY ([s4279-diff]) and the store ring ([s4279-ring]). Idempotent."""
import subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
subprocess.check_call([sys.executable, str(R / "tools" / "apply_s4279_nodeinvariant.py")])
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
if "s4279-ring" not in t:
    a = "    if (rs64_s4222_on()) {\n        uint32_t np = addr & 0x1FFFFFFFu;\n        if (np >= 0x1F9C00u && np < 0x1FB400u) {\n"
    assert t.count(a) == 1
    t = t.replace(a, a + "            s4279_ring_push(pc, addr, width);\n", 1)
    fn = r'''
static struct { uint32_t pc, addr, n; char w; } s4279_rg[96]; static unsigned s4279_rgi = 0;
static void s4279_ring_push(uint32_t pc, uint32_t addr, char w) { auto& e = s4279_rg[s4279_rgi++ % 96]; e.pc = pc; e.addr = addr; e.n = rs64_s4234_g; e.w = w; }
extern "C" void rs64_s4279_dump_ring(void) {
    std::fprintf(stderr, "[s4279-ring] last 96 node-region stores (oldest first)\n");
    for (unsigned k = 0; k < 96; k++) { auto& e = s4279_rg[(s4279_rgi + k) % 96]; if (e.pc) std::fprintf(stderr, "[s4279-ring] n=%u pc=%08X %c addr=%08X\n", e.n, e.pc, e.w, e.addr); }
}
'''
    b = 'extern "C" void rs64_s4222_store_watch('
    assert t.count(b) == 1
    t = t.replace(b, fn + b, 1)
    f.write_text(t)
p = RF / "funcs_24.c"
s = p.read_text()
if "s4279-diff" not in s:
    endmark = "tl ? (uint32_t)MEM_W(4, S32(tl)) : 0u); } }\n"
    assert s.count(endmark) == 1
    j = s.index(endmark) + len(endmark)
    code = r'''    { /* PATCH: s4279-diff */ static uint32_t sh[1536]; static int dumped = 0, have = 0; extern void rs64_s4279_dump_ring(void);
      uint32_t cs[1536]; for (unsigned k = 0; k < 1536; k++) cs[k] = (uint32_t)MEM_W(0, S32(0x801F9C00u + 4u * k));
      { uint32_t hd2 = (uint32_t)MEM_W(-0X661C, S32(0X8015 << 16)), tl2 = (uint32_t)MEM_W(-0X664C, S32(0X8015 << 16)); uint32_t c2 = tl2; uint32_t pn = 0; int b2 = 0; unsigned l2 = 0;
        while (c2 && l2 < 400 && c2 >= 0x801F9C00u && c2 < 0x801FB400u) { if (cs[(c2 - 0x801F9C00u) / 4] != pn) b2 = 1; pn = c2; c2 = cs[(c2 - 0x801F9C00u) / 4 + 1]; ++l2; }
        if (tl2 && (b2 || pn != hd2) && have && !dumped) { dumped = 1;
          fprintf(stderr, "[s4279-diff] first BAD at ENTRY n=%u; changed words since previous ENTRY (addr old new):\n", rs64_s4234_g);
          for (unsigned k = 0; k < 1536; k++) if (cs[k] != sh[k]) fprintf(stderr, "[s4279-diff] %08X %08X -> %08X\n", 0x801F9C00u + 4u * k, sh[k], cs[k]);
          rs64_s4279_dump_ring(); } }
      memcpy(sh, cs, sizeof sh); have = 1; }
'''
    s = s[:j] + code + s[j:]
    p.write_text(s)
print("ok")
