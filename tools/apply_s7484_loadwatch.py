"""s7484 class EI: guest LOADS from freed rs_malloc blocks (use-after-free reads), load-side twin of the s7480 store watch.

Every generated guest load statement of the exact form `ctx->X = MEM_W|MEM_H|MEM_HU|MEM_B|MEM_BU|LD(a, b);` whose preceding
line is the recompiler's `// 0x<pc>: <lw|lwc1|lh|lhu|lb|lbu|ld|ldc1> ...` comment is wrapped as
`{ RS64_S7484_LD(pc, a, b, w); <load> }` (the check runs BEFORE the load, so a load whose destination is its own base register
still tests the right address). The macro is a single predicted-false branch on g_rs64_s7484_on (set host-side only under
ROGUESQ_S7484_UAFLOAD=1 + ROGUESQ_S7480_UAF=1 + ROGUESQ_S7475_CANARY=1); when on it tests the first/last byte of the access in
the s7475/s7480 bitmap g_rs64_s7475_bm (slack + freed ranges) and calls rs64_s7484_load(pc, a, w, fn) on a marked byte.
Not covered: lwl/lwr/ldl/ldr (do_lwl helpers), host-side readers, loads in hand-written PATCH code.
Measurement only: no game value is changed. Idempotent; registered in fixup_game_funcs_vendored.py."""
from pathlib import Path
import re
import sys

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7484 loadwatch"
HDR = ("/* " + MARK + " */\n"
       "extern int g_rs64_s7484_on; extern unsigned char* g_rs64_s7475_bm;\n"
       "extern int rs64_s7484_load(uint32_t pc, uint32_t a, int w, const char* fn);\n"
       "#define RS64_S7484_LD(pc, x, y, w) do { if (__builtin_expect(g_rs64_s7484_on, 0)) { const uint32_t _o7484 = (uint32_t)((x) + (y)) - 0x80000000u; "
       "if (_o7484 < 0x17FFFF0u && (((g_rs64_s7475_bm[_o7484 >> 3] >> (_o7484 & 7u)) | (g_rs64_s7475_bm[(_o7484 + (w) - 1u) >> 3] >> ((_o7484 + (w) - 1u) & 7u))) & 1u)) "
       "rs64_s7484_load((pc), _o7484 + 0x80000000u, (w), __func__); } } while (0)\n")
W = {"lw": 4, "lwc1": 4, "lh": 2, "lhu": 2, "lb": 1, "lbu": 1, "ld": 8, "ldc1": 8}
OPS = {"MEM_W": (4,), "MEM_H": (2,), "MEM_HU": (2,), "MEM_B": (1,), "MEM_BU": (1,), "LD": (8,)}
CMT = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}): (\w+)\s")
LOAD = re.compile(r"^(\s*)(ctx->(?:r\d+|f\d+\.u32l|f\d+\.u64) = (MEM_W|MEM_H|MEM_HU|MEM_B|MEM_BU|LD)\(([^,();]+), ([^,();]+)\);)\s*$")
tot = files = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if MARK in t:
        continue
    lines = t.split("\n"); k = 0
    for i in range(1, len(lines)):
        m = LOAD.match(lines[i])
        if not m:
            continue
        c = CMT.match(lines[i - 1])
        if not c or c.group(2) not in W or W[c.group(2)] not in OPS[m.group(3)]:
            continue
        lines[i] = "%s{ RS64_S7484_LD(0x%su, %s, %s, %d); %s }" % (m.group(1), c.group(1).upper(), m.group(4), m.group(5), W[c.group(2)], m.group(2))
        k += 1
    if k:
        t = "\n".join(lines)
        assert '#include "recomp.h"\n' in t, p
        t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + HDR, 1)
        p.write_text(t); tot += k; files += 1
print("s7484 loadwatch: wrapped", tot, "loads in", files, "files")
