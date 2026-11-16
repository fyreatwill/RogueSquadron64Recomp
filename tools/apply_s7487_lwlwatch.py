"""s7487 class EL: guest UNALIGNED loads (lwl/lwr) from freed rs_malloc blocks, the gap s7484 EI left (do_lwl helpers unwrapped).

Census (s7487, this regen): 207 lwl + 203 lwr generated sites, 0 ldl/ldr. Every statement of the exact form
`ctx->rN = do_lwl|do_lwr(rdram, <init>, <base>, <imm>);` whose preceding line is the recompiler's `// 0x<pc>: lwl|lwr ...`
comment is wrapped as `{ RS64_S7487_LWX(pc, idx, base, imm, isl); <load> }`. The test runs BEFORE the load and uses the bytes the
instruction really reads: lwl at a reads [a, a|3], lwr at a reads [a&~3, a]. Gate g_rs64_s7487_on (host: ROGUESQ_S7487_LWLWATCH=1 on
top of the s7484 load watch). When on: g_rs64_s7487_cnt[idx]++ (execution census), a marked byte in g_rs64_s7475_bm routes to
rs64_s7487_lwx(..., marked=1) -> the s7484 freed-record classifier; every 64th execution per site is sampled (marked=0) for the
live-heap census and the EL positive control (ROGUESQ_S7487_LWLCTL=<s>: plant a LIVE heap block an lwl/lwr just read).
Measurement only: no game value is changed. Idempotent; registered in fixup_game_funcs_vendored.py after apply_s7484_loadwatch.py."""
from pathlib import Path
import re
import sys

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7487 lwlwatch"
HDR = ("/* " + MARK + " */\n"
       "extern int g_rs64_s7487_on; extern unsigned char* g_rs64_s7475_bm; extern unsigned int g_rs64_s7487_cnt[];\n"
       "extern int rs64_s7487_lwx(uint32_t pc, int idx, uint32_t a, int w, const char* fn, int marked);\n"
       "#define RS64_S7487_LWX(pc, idx, x, y, isl) do { if (__builtin_expect(g_rs64_s7487_on, 0)) { const uint32_t _a7487 = (uint32_t)((x) + (y)); "
       "const uint32_t _l7487 = (isl) ? _a7487 : (_a7487 & ~3u); const uint32_t _w7487 = (isl) ? (4u - (_a7487 & 3u)) : ((_a7487 & 3u) + 1u); "
       "const uint32_t _o7487 = _l7487 - 0x80000000u; const unsigned int _c7487 = ++g_rs64_s7487_cnt[(idx)]; "
       "if (_o7487 < 0x17FFFF0u && (((g_rs64_s7475_bm[_o7487 >> 3] >> (_o7487 & 7u)) | (g_rs64_s7475_bm[(_o7487 + _w7487 - 1u) >> 3] >> ((_o7487 + _w7487 - 1u) & 7u))) & 1u)) "
       "rs64_s7487_lwx((pc), (idx), _l7487, (int)_w7487, __func__, 1); else if ((_c7487 & 63u) == 1u) rs64_s7487_lwx((pc), (idx), _l7487, (int)_w7487, __func__, 0); } } while (0)\n")
CMT = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}): (lwl|lwr)\s")
LOAD = re.compile(r"(ctx->r\d+ = do_(lwl|lwr)\(rdram, ([^,();]+), ([^,();]+), ([^,();]+)\);)")
PCL = re.compile(r"^\s*g_rs64_last_guest_pc = 0x[0-9A-Fa-f]{8}u;\s*$")
DONE = re.compile(r"RS64_S7487_LWX\(0x[0-9A-F]{8}u, (\d+),")
CAP = 1024
files_l = sorted(D.glob("funcs_*.c"))
idx = 1 + max([int(x) for p in files_l for x in DONE.findall(p.read_text())] or [-1])  # per-site idempotence: new sites continue the index
tot = files = 0; skipped = 0; kinds = {"lwl": 0, "lwr": 0}
for p in files_l:
    t = p.read_text()
    lines = t.split("\n"); k = 0
    for i in range(1, len(lines)):
        if "RS64_S7487_LWX(" in lines[i]:
            skipped += 1
            continue
        c = CMT.match(lines[i - 1])
        if not c and i >= 2 and PCL.match(lines[i - 1]):
            c = CMT.match(lines[i - 2])
        if not c:
            continue
        ms = list(LOAD.finditer(lines[i]))
        if len(ms) != 1 or ms[0].group(2) != c.group(2):
            continue
        m = ms[0]
        assert idx < CAP, "s7487: more lwl/lwr sites than g_rs64_s7487_cnt holds"
        rep = "{ RS64_S7487_LWX(0x%su, %d, %s, %s, %d); %s }" % (c.group(1).upper(), idx, m.group(4), m.group(5), 1 if m.group(2) == "lwl" else 0, m.group(1))
        lines[i] = lines[i][:m.start()] + rep + lines[i][m.end():]
        idx += 1; k += 1; kinds[m.group(2)] += 1
    if k:
        t = "\n".join(lines)
        if MARK not in t:
            assert '#include "recomp.h"\n' in t, p
            t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + HDR, 1)
        p.write_text(t); tot += k; files += 1
print("s7487 lwlwatch: wrapped", tot, "unaligned loads (lwl %d, lwr %d) in" % (kinds["lwl"], kinds["lwr"]), files, "files; already-wrapped sites", skipped)
