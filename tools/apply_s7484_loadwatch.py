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
W = {"lwu": 4, "lw": 4, "lwc1": 4, "lh": 2, "lhu": 2, "lb": 1, "lbu": 1, "ld": 8, "ldc1": 8}
OPS = {"MEM_WU": (4,), "MEM_W": (4,), "MEM_H": (2,), "MEM_HU": (2,), "MEM_B": (1,), "MEM_BU": (1,), "LD": (8,)}
CMT = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}): (\w+)\s")
LOAD = re.compile(r"^(\s*)(ctx->(?:r\d+|f\d+\.u32l|f\d+\.u64) = (MEM_WU|MEM_W|MEM_H|MEM_HU|MEM_B|MEM_BU|LD)\(([^,();]+), ([^,();]+)\);)\s*$")
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

# s7786 per-site pass (idempotent per site, runs on every file): the pass above needs the comment on the line directly above the
# load, so it missed 4534 loads (tools/s7786_load_hook_reg_census.py): loads in pc-traced functions (a `g_rs64_last_guest_pc = ..;`
# line between), every ldc1 (a `CHECK_FR(ctx, N);` line between), and loads already inside an s4307 synth-read block
# `{ uint32_t s4575_a = U32(ADD32(R, OFF)); ...` (incl. the s4984 atomic voice-count loads). Same macro, same check-before-load.
SKIP = re.compile(r"^\s*(?:g_rs64_last_guest_pc = 0x[0-9A-Fa-f]{8}u;|CHECK_FR\(ctx, \d+\);)\s*$")
INL = re.compile(r"\b(MEM_WU|MEM_W|MEM_HU|MEM_H|MEM_BU|MEM_B|LD)\((ctx->r\d+), (-?0X[0-9A-Fa-f]+|-?\d+)\)")
J43 = re.compile(r"^(\s*)\{ (uint32_t s4575_a = U32\(ADD32\(([^,();]+), ([^,();]+)\)\);.*)$")
tot2 = files2 = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text(); lines = t.split("\n"); k = 0
    for i in range(1, len(lines)):
        m = LOAD.match(lines[i]); j = None if m else J43.match(lines[i]); x = None
        if not m and not j:
            # s7786c: a load sharing its line with patch code (s7024/s6493 trailers, s6883 host edge read): exactly one
            # MEM_x(base, off) on a brace-balanced line directly under its pc comment -> wrap the whole line, hook first
            c0 = CMT.match(lines[i - 1]); L = lines[i]
            ms = list(INL.finditer(L))
            if (c0 and c0.group(2) in W and len(ms) == 1 and W[c0.group(2)] in OPS[ms[0].group(1)] and "RS64_S7484_LD(" not in L
                    and L.count("{") == L.count("}") and L.count("(") == L.count(")")):
                q = i + 1   # the real guest load may follow on its own line (s7064 poll reads the same word first): wrap that
                while q < len(lines) and q - i < 60 and not CMT.match(lines[q]) and not LOAD.match(lines[q]) and not J43.match(lines[q]):
                    q += 1
                if q < len(lines) and (LOAD.match(lines[q]) or J43.match(lines[q])):
                    continue
                x = ms[0]
            else:
                continue
        b = i - 1
        while b > 0 and i - b < 60 and not CMT.match(lines[b]):
            # s7786b: walk over pc-trace / CHECK_FR / hand-written PATCH lines to the load's own pc comment; stop at another
            # bare guest load or a function start (then the pc is not this load's)
            if LOAD.match(lines[b]) or J43.match(lines[b]) or lines[b].startswith("RECOMP_FUNC") or "RS64_S7484_LD(0x" in lines[b]:
                b = 0; break
            b -= 1
        c = CMT.match(lines[b])
        if not c or c.group(2) not in W:
            continue
        if x:
            ind = L[:len(L) - len(L.lstrip())]
            lines[i] = "%s{ RS64_S7484_LD(0x%su, %s, %s, %d); %s }" % (ind, c.group(1).upper(), x.group(2), x.group(3), W[c.group(2)], L.strip())
        elif m:
            if W[c.group(2)] not in OPS[m.group(3)]:
                continue
            lines[i] = "%s{ RS64_S7484_LD(0x%su, %s, %s, %d); %s }" % (m.group(1), c.group(1).upper(), m.group(4), m.group(5), W[c.group(2)], m.group(2))
        else:
            lines[i] = "%s{ RS64_S7484_LD(0x%su, %s, %s, %d); %s" % (j.group(1), c.group(1).upper(), j.group(3), j.group(4), W[c.group(2)], j.group(2))
        k += 1
    if k:
        t = "\n".join(lines)
        if MARK not in t:
            assert '#include "recomp.h"\n' in t, p
            t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + HDR, 1)
        p.write_text(t); tot2 += k; files2 += 1
print("s7484 loadwatch s7786 pass: wrapped", tot2, "more loads in", files2, "files")
