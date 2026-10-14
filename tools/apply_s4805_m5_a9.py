#!/usr/bin/env python3
"""Add the M5 A9 audit instrument to the generated voice-array base guards.

Every A9 guard (13 sites in funcs_24.c) keeps its bail behaviour. The condition
now calls rs64_s4805_a9_bad(), which counts checks / bad values per site and
supports a same-run positive control (ROGUESQ_A9_FORCE_BAD=N makes the first N
checks per site take the bail path). The sole publisher of 0x801496F8
(allocateSongChannelArray, 0x8008F0EC) is logged in funcs_23.c. No pointer is
ever forced; the force arm only takes the guard's own existing bail.
"""
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")

HELPER = r'''
/* PATCH: s4805 M5 A9 audit. ROGUESQ_LOG_M5_A9 (or LOG_ALL) logs; ROGUESQ_A9_FORCE_BAD=N is the positive control. */
static int rs64_s4805_a9_bad(const char* site, uint32_t v, uint32_t ra) {
    static int init = 0, log = 0; static unsigned force = 0;
    static struct { const char* site; unsigned checks, bad, forced; } t[32];
    static int nt = 0;
    if (!init) {
        const char* e = getenv("ROGUESQ_LOG_M5_A9"); const char* a = getenv("ROGUESQ_LOG_ALL");
        const char* f = getenv("ROGUESQ_A9_FORCE_BAD");
        log = ((e && e[0] && e[0] != '0') || (a && a[0] && a[0] != '0')) ? 1 : 0;
        force = f ? (unsigned)strtoul(f, NULL, 0) : 0u;
        init = 1;
    }
    int i = 0;
    for (; i < nt; i++) if (t[i].site == site) break;
    if (i == nt) { if (nt >= 32) return (v < 0x80000000u || v >= 0x80800000u); t[nt].site = site; nt++; }
    t[i].checks++;
    int bad = (v < 0x80000000u || v >= 0x80800000u);
    if (bad) t[i].bad++;
    int forced = 0;
    if (!bad && t[i].forced < force) { t[i].forced++; forced = 1; }
    if (log && (((t[i].checks & (t[i].checks - 1)) == 0) || bad || forced)) {
        fprintf(stderr, "[m5-a9] site=%s checks=%u bad=%u forced=%u val=0x%08X ra=0x%08X\n",
                site, t[i].checks, t[i].bad, t[i].forced, v, ra);
        fflush(stderr);
    }
    return bad || forced;
}
'''

WRITER_HELPER = r'''
/* PATCH: s4805 M5 A9 writer row. ORIGIN: guest allocateSongChannelArray (0x8008F0EC) is the sole publisher of 0x801496F8. */
static void rs64_s4805_a9_writer(uint32_t value, uint32_t ra) {
    static int init = 0, log = 0; static unsigned rows = 0;
    if (!init) { const char* e = getenv("ROGUESQ_LOG_M5_A9"); const char* a = getenv("ROGUESQ_LOG_ALL");
        log = ((e && e[0] && e[0] != '0') || (a && a[0] && a[0] != '0')) ? 1 : 0; init = 1; }
    if (!log || rows >= 32u) return;
    fprintf(stderr, "[m5-a9-writer] n=%u pc=0x8008F0EC addr=0x801496F8 value=0x%08X ra=0x%08X\n", rows++, value, ra);
    fflush(stderr);
}
'''

COND = re.compile(
    r"^(\s*)if \((voice_base_r\d+_([0-9A-F]{8})|r2_lo) < 0x80000000u \|\| \2 >= 0x80800000u\) \{\n$")


def patch_funcs_24(path: Path) -> int:
    text = path.read_text()
    if "PATCH: s4805 M5 A9 audit" not in text:
        text = text.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + HELPER, 1)
    out, n = [], 0
    for line in text.splitlines(True):
        m = COND.match(line)
        if m:
            site = "0x" + m.group(3) if m.group(3) else "isAudioSlotActive"
            line = f'{m.group(1)}if (rs64_s4805_a9_bad("{site}", {m.group(2)}, U32(ctx->r31))) {{\n'
            n += 1
        out.append(line)
    path.write_text(''.join(out))
    return n


def patch_funcs_23(path: Path) -> int:
    text = path.read_text()
    if "rs64_s4805_a9_writer" in text:
        return 0
    text = text.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + WRITER_HELPER, 1)
    needle = "rs64_m5_lowfield_store('W', 0x8008F0ECu, U32(ADD32(ctx->r1, -0X6908)), U32(ctx->r2)); /* PATCH: s4340 lowfield writer */\n"
    if needle not in text:
        raise SystemExit("funcs_23.c: A9 writer anchor missing")
    text = text.replace(needle, needle + "    rs64_s4805_a9_writer(U32(ctx->r2), U32(ctx->r31));\n", 1)
    path.write_text(text)
    return 1


n = patch_funcs_24(ROOT / "funcs_24.c")
w = patch_funcs_23(ROOT / "funcs_23.c")
if n != 13 and n != 0:
    raise SystemExit(f"A9 guard sites rewritten: {n}, expected 13")
print(f"s4805 A9 instrumented {n} guard sites; writer patch={w}")
