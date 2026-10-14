#!/usr/bin/env python3
"""Add the regeneration-safe A10 audit arm to the generated audio readers.

The generated files live beside this repository, so this script is the small
post-fixup stage for the current checked-out output.  It keeps the guard in
the default arm and makes the guard-off arm explicit; it never edits a bail
target or forces a pointer value.
"""
from pathlib import Path
import re
import sys


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"
)

HELPER = r'''
/* PATCH: s4681 M5 A10 audit. ROGUESQ_A10_GUARD_OFF is an experiment arm. */
static int rs64_s4681_a10_off = -1;
static int rs64_s4681_a10_enabled(void) {
    if (rs64_s4681_a10_off < 0) {
        const char* e = getenv("ROGUESQ_A10_GUARD_OFF");
        rs64_s4681_a10_off = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    return rs64_s4681_a10_off;
}
static void rs64_s4681_a10_observe(const char* family, const char* site,
                                   uint32_t value, uint32_t ra) {
    static int enabled = -1;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_A10");
        const char* a = getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (a && a[0] && a[0] != '0')) ? 1 : 0;
    }
    if (!enabled || rows >= 256u) return;
    fprintf(stderr, "[m5-a10-guard] n=%u family=%s site=%s ptr=0x%08X ra=0x%08X off=%u\n",
            rows++, family, site, value, ra, rs64_s4681_a10_enabled());
    fflush(stderr);
}
static void rs64_s4681_a10_writer(uint32_t value, uint32_t ra) {
    static int enabled = -1;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_A10");
        const char* a = getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (a && a[0] && a[0] != '0')) ? 1 : 0;
    }
    if (!enabled || rows >= 32u) return;
    fprintf(stderr, "[m5-a10-writer] n=%u pc=0x80096D88 addr=0x801529C0 value=0x%08X ra=0x%08X\n",
            rows++, value, ra);
    fflush(stderr);
}
'''


def patch_file(path: Path) -> int:
    text = path.read_text()
    if "PATCH: s4681 M5 A10 audit" not in text:
        text = text.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + HELPER, 1)
    lines = text.splitlines(True)
    out = []
    family = None
    patched = 0
    for line in lines:
        if "song-tick-table pointer guard" in line:
            family = "songtempo"
            m = re.search(r"site=([^ )]+)", line)
            site = m.group(1) if m else "unknown"
        elif "voice-list-node pointer range guard" in line:
            family = "voice-list"
            site = "tick-reap-3d-voices"
        out.append(line)
        if family and "!rs64_s4681_a10_enabled" not in line and re.match(
            r"\s*if \([^\n]*(?:_lo_|r\d+_lo)[^\n]*\) \{\n$", line
        ):
            indent = line[: len(line) - len(line.lstrip())]
            condition = line.strip()[3:-3]
            reg = re.search(r"(r\d+)_lo(?:_|\b)", condition)
            value = f"U32(ctx->{reg.group(1)})" if reg else "0u"
            if family == "voice-list":
                value = "U32(ctx->r16)"
            out.insert(len(out) - 1,
                       f'{indent}rs64_s4681_a10_observe("{family}", "{site}", {value}, U32(ctx->r31));\n')
            out[-1] = f"{indent}if (!rs64_s4681_a10_enabled() && ({condition})) {{\n"
            patched += 1
            family = None
    text = ''.join(out)
    text = text.replace("&& ((", "&& (")
    if path.name == "funcs_25.c" and "rs64_s4681_a10_writer(U32(ctx->r2)" not in text:
        needle = "    MEM_W(0X29C0, ctx->r1) = ctx->r2;\n"
        if needle not in text:
            raise SystemExit(f"{path}: A10 writer anchor missing")
        text = text.replace(needle, needle + "    rs64_s4681_a10_writer(U32(ctx->r2), U32(ctx->r31)); /* ORIGIN: guest writer 0x80096D88 publishes 0x801529C0 */\n", 1)
    path.write_text(text)
    return patched


total = 0
for name in ("funcs_25.c", "funcs_26.c"):
    total += patch_file(ROOT / name)
# Fresh-regen trees patch every site (44), an already-patched tree patches 0:
# the active==remaining check below is the real verification.
remaining = sum(
    text.count("song-tick-table pointer guard") + text.count("voice-list-node pointer range guard")
    for text in (p.read_text() for p in (ROOT / "funcs_25.c", ROOT / "funcs_26.c"))
)
active = sum(
    text.count("!rs64_s4681_a10_enabled")
    for text in (p.read_text() for p in (ROOT / "funcs_25.c", ROOT / "funcs_26.c"))
)
if active != remaining:
    raise SystemExit(f"A10 verification mismatch: markers={remaining} active={active}")
print(f"s4681 A10 patched {total} remaining guard sites; verified {active} total")
