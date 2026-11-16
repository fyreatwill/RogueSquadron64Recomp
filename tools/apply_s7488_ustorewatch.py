"""s7488 class EM: guest UNALIGNED STORES (swl/swr) into freed rs_malloc blocks or canary slack, the gap EG/EH left: the s5660 hook
(rs64_s5660_ustore) gets only the aligned word and never reaches rs64_s7475_store, so the s7475 canary, s7479 pad and s7480 UAF store
watches were blind to swl/swr.

Census (s7488, this regen): 203 swl + 202 swr generated sites, 0 sdl/sdr; 404 carry the s5660 hook, the one without it is
`swl $zero, 0x0($a0)` (`do_swl(rdram, 0X0, ctx->r4, 0);`). Every statement `do_swl|do_swr(rdram, <off>, <base>, <val>);` whose
recompiler comment `// 0x<pc>: swl|swr ...` sits within the 3 preceding lines (skipping the s5660 PATCH line and g_rs64_last_guest_pc
lines) is wrapped as `{ RS64_S7488_UST(pc, idx, base, off, isl); <store> }`. The test runs BEFORE the store and uses the bytes the
instruction really writes: swl at a writes [a, a|3], swr at a writes [a&~3, a]. Gate g_rs64_s7488_on (host: ROGUESQ_S7488_USTOREWATCH=1
on top of ROGUESQ_S7475_CANARY=1 + ROGUESQ_S7480_UAF=1). When on: g_rs64_s7488_cnt[idx]++ (execution census); a marked byte in
g_rs64_s7475_bm routes to rs64_s7488_ust(..., marked=1) -> rs64_s7475_store (s7480 freed-record classifier + s7475 slack canary);
every 64th execution per site is sampled (marked=0) for the live-heap census and the EM control (ROGUESQ_S7488_USTCTL=<s>: record a
LIVE heap block an swl/swr just wrote as freed; the next swl/swr into it MUST log `[s7488] ust-ctl DETECTED`).
Measurement only: no game value is changed. Idempotent; registered in fixup_game_funcs_vendored.py after apply_s7487_lwlwatch.py."""
from pathlib import Path
import re
import sys

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7488 ustorewatch"
HDR = ("/* " + MARK + " */\n"
       "extern int g_rs64_s7488_on; extern unsigned char* g_rs64_s7475_bm; extern unsigned int g_rs64_s7488_cnt[];\n"
       "extern int rs64_s7488_ust(uint32_t pc, int idx, uint32_t a, int w, const char* fn, int marked);\n"
       "#define RS64_S7488_UST(pc, idx, x, y, isl) do { if (__builtin_expect(g_rs64_s7488_on, 0)) { const uint32_t _a7488 = (uint32_t)((x) + (y)); "
       "const uint32_t _l7488 = (isl) ? _a7488 : (_a7488 & ~3u); const uint32_t _w7488 = (isl) ? (4u - (_a7488 & 3u)) : ((_a7488 & 3u) + 1u); "
       "const uint32_t _o7488 = _l7488 - 0x80000000u; const unsigned int _c7488 = ++g_rs64_s7488_cnt[(idx)]; "
       "if (_o7488 < 0x17FFFF0u && (((g_rs64_s7475_bm[_o7488 >> 3] >> (_o7488 & 7u)) | (g_rs64_s7475_bm[(_o7488 + _w7488 - 1u) >> 3] >> ((_o7488 + _w7488 - 1u) & 7u))) & 1u)) "
       "rs64_s7488_ust((pc), (idx), _l7488, (int)_w7488, __func__, 1); else if ((_c7488 & 63u) == 1u) rs64_s7488_ust((pc), (idx), _l7488, (int)_w7488, __func__, 0); } } while (0)\n")
CMT = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}): (swl|swr|sdl|sdr)\s")
SKIP = re.compile(r"^\s*(g_rs64_last_guest_pc = 0x[0-9A-Fa-f]{8}u;|\{ uint32_t s5660_a = .*PATCH: s5660 \*/)\s*$")
STORE = re.compile(r"(do_(swl|swr)\(rdram, ([^,();]+), ([^,();]+), ([^,();]+)\);)")
DONE = re.compile(r"RS64_S7488_UST\(0x[0-9A-F]{8}u, (\d+),")
CAP = 1024
files_l = sorted(D.glob("funcs_*.c"))
idx = 1 + max([int(x) for p in files_l for x in DONE.findall(p.read_text())] or [-1])
tot = files = skipped = 0; kinds = {"swl": 0, "swr": 0}; cmts = {"swl": 0, "swr": 0, "sdl": 0, "sdr": 0}; nohook = []
for p in files_l:
    t = p.read_text()
    lines = t.split("\n"); k = 0
    for ln in lines:
        c = CMT.match(ln)
        if c: cmts[c.group(2)] += 1
    for i in range(1, len(lines)):
        if "RS64_S7488_UST(" in lines[i]:
            skipped += 1
            continue
        ms = list(STORE.finditer(lines[i]))
        if len(ms) != 1:
            continue
        c = None; j = i - 1; hooked = False
        while j >= max(0, i - 3):
            c = CMT.match(lines[j])
            if c: break
            if not SKIP.match(lines[j]): break
            if "s5660" in lines[j]: hooked = True
            j -= 1
        if not c or c.group(2) != ms[0].group(2):
            continue
        m = ms[0]
        assert idx < CAP, "s7488: more swl/swr sites than g_rs64_s7488_cnt holds"
        if not hooked: nohook.append("%s %s %s" % (p.name, c.group(1).upper(), m.group(1)))
        rep = "{ RS64_S7488_UST(0x%su, %d, %s, %s, %d); %s }" % (c.group(1).upper(), idx, m.group(4), m.group(3), 1 if m.group(2) == "swl" else 0, m.group(1))
        lines[i] = lines[i][:m.start()] + rep + lines[i][m.end():]
        idx += 1; k += 1; kinds[m.group(2)] += 1
    if k:
        t = "\n".join(lines)
        if MARK not in t:
            assert '#include "recomp.h"\n' in t, p
            t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + HDR, 1)
        p.write_text(t); tot += k; files += 1
print("s7488 ustorewatch: wrapped", tot, "unaligned stores (swl %d, swr %d) in" % (kinds["swl"], kinds["swr"]), files, "files; already-wrapped", skipped,
      "; comments", cmts, "; without s5660 hook", nohook)
