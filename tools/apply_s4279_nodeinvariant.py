#!/usr/bin/env python3
"""s4279: find what breaks the sample-stream LRU list (head->next==0 while head!=tail) BEFORE the pool hits 0.
(1) ENTRY invariant walk in fillSampleStreamRange: tail->prev chain, each node's next must equal the previously visited
    node, chain end must equal head; logs [s4279-chk] every 500 calls (positive control: len vs bump progress) and
    [s4279-BAD] on violation (first 40 rows).
(2) store watch widened to the node region 0x1F9D10..0x1FB2D8: stores from PCs outside the list-op code
    0x8008F780..0x8008FF00 are logged [s4279-foreign] (budget 400, with ENTRY n); in-code stores are only counted
    ([s4279-own], control that the watch fires).
Needs ROGUESQ_LOG_S4222=1. Applies apply_s4278_headwriter.py first. Idempotent."""
import subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
subprocess.check_call([sys.executable, str(R / "tools" / "apply_s4278_headwriter.py")])
OLDR = "sw_p >= 0x1499B0u && sw_p < 0x1499E8u"
NEWR = "(sw_p >= 0x1499B0u && sw_p < 0x1499E8u) || (sw_p >= 0x1F9C00u && sw_p < 0x1FB400u)"
n = 0
for q in sorted(RF.glob("funcs_*.c")):
    c = q.read_text()
    if OLDR in c and NEWR not in c:
        q.write_text(c.replace(OLDR, NEWR)); n += 1
print("widened", n)
f = R / "src/main/upstream_compat.cpp"
t = f.read_text()
if "s4279-foreign" not in t:
    a = "    if (!rs64_s4222_on() || rs64_s4234_g < 9400u) return;\n    static int rows = 0;"
    assert t.count(a) == 1
    b = r'''    if (rs64_s4222_on()) {
        uint32_t np = addr & 0x1FFFFFFFu;
        if (np >= 0x1F9C00u && np < 0x1FB400u) {
            static unsigned long own = 0; static int frows = 0;
            if (pc >= 0x8008F780u && pc < 0x8008FF00u) {
                ++own;
                if (own == 1 || own == 100 || (own % 20000) == 0)
                    std::fprintf(stderr, "[s4279-own] n=%u cnt=%lu pc=%08X addr=%08X\n", rs64_s4234_g, own, pc, addr);
            } else if (frows < 400) {
                ++frows;
                std::fprintf(stderr, "[s4279-foreign] n=%u pc=%08X %c addr=%08X val=%08X\n", rs64_s4234_g, pc, width, addr, value);
            }
            return;
        }
    }
'''
    t = t.replace(a, b + a, 1)
    f.write_text(t)
p = RF / "funcs_24.c"
s = p.read_text()
if "s4279-chk" not in s:
    anchor = "/* PATCH: s4234 entry */\n"
    assert s.count(anchor) == 1
    code = r'''    { /* PATCH: s4279 invariant */ static int s4279_rows = 0; uint32_t hd = (uint32_t)MEM_W(-0X661C, S32(0X8015 << 16)), tl = (uint32_t)MEM_W(-0X664C, S32(0X8015 << 16)), pl = (uint32_t)MEM_W(-0X6634, S32(0X8015 << 16));
      uint32_t cur = tl, prevn = 0, bad = 0, firstbad = 0, last = 0; unsigned len = 0, plen = 0;
      while (cur && len < 400) { if (cur < 0x801F9C00u || cur >= 0x801FB400u) { bad |= 8; firstbad = firstbad ? firstbad : cur; break; }
        uint32_t nx = (uint32_t)MEM_W(0, S32(cur)), pv = (uint32_t)MEM_W(4, S32(cur)); if (nx != prevn) { bad |= 1; firstbad = firstbad ? firstbad : cur; } last = cur; prevn = cur; cur = pv; ++len; }
      if (len >= 400) bad |= 4; else if (tl && last != hd) { bad |= 2; if (!firstbad) firstbad = last; }
      { uint32_t pc2 = pl; while (pc2 && plen < 400 && pc2 >= 0x801F9C00u && pc2 < 0x801FB400u) { pc2 = (uint32_t)MEM_W(0, S32(pc2)); ++plen; } }
      if (bad ? s4279_rows < 40 : (rs64_s4234_g % 500 == 0 || rs64_s4234_g <= 3)) { if (bad) ++s4279_rows;
        fprintf(stderr, "[%s] n=%u bad=%u len=%u poollen=%u head=%08X tail=%08X pool=%08X firstbad=%08X fb.next=%08X fb.prev=%08X head.next=%08X tail.prev=%08X\n", bad ? "s4279-BAD" : "s4279-chk", rs64_s4234_g, bad, len, plen, hd, tl, pl, firstbad,
          firstbad ? (uint32_t)MEM_W(0, S32(firstbad)) : 0u, firstbad ? (uint32_t)MEM_W(4, S32(firstbad)) : 0u, hd ? (uint32_t)MEM_W(0, S32(hd)) : 0u, tl ? (uint32_t)MEM_W(4, S32(tl)) : 0u); } }
'''
    s = s.replace(anchor, anchor + code, 1)
    p.write_text(s)
print("ok")
