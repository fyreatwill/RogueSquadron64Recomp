"""s5774: name which direct jal calls spawnSceneDebrisAndEffectCluster.

Static census: entry 0x800B01E4, exactly five ROM jal encodings, zero raw
pointers and zero j encodings. Recompiled r31 is not a caller, so each jal
site logs itself. A player-slot call whose state halfword does not yet have
bit 0x10 is the kill-store predecessor (the sh at 0x800B0348 sets that bit).

Gated by ROGUESQ_LOG_MTM. Shares rs64_s5773_ord/ms with [killset]/[lives].
"""
import pathlib
import sys

TAG = "PATCH: s5774 debris caller"

SITES = {
    "0x800B0C34": (0, "updateSplineCraftTransform"),
    "0x800B0D9C": (1, "updateSplineCraftTransform"),
    "0x800B0EBC": (2, "updateSplineCraftTransform"),
    "0x800B2A08": (3, "updatePlayerCraftPhysics"),
    "0x800B2EC4": (4, "updatePlayerCraftPhysics"),
}

HELPER = """/* """ + TAG + """ */
static unsigned s5774_c[5];
static unsigned s5774_total;
static int s5774_e = -1;
static unsigned s5774_pre_left = 24;
static unsigned s5774_pl_left = 10;
static unsigned s5774_np_left = 12;
static void s5774_debris_log(uint8_t* rdram, recomp_context* ctx, unsigned site, int idx, const char* fn) {
    if (s5774_e < 0) {
        const char* e = getenv("ROGUESQ_LOG_MTM");
        s5774_e = (e && e[0]) ? 1 : 0;
    }
    if (!s5774_e || idx < 0 || idx > 4) return;
    unsigned a0 = (unsigned)U32(ctx->r4);
    unsigned hw = (unsigned)MEM_HU(ctx->r4, 0x180);
    int player = (a0 == 0x80137DBCu);
    int prekill = player && ((hw & 0x10u) == 0u);
    s5774_c[idx]++;
    s5774_total++;
    int emit = 0;
    const char* kind = "census";
    if (prekill && s5774_pre_left) { s5774_pre_left--; emit = 1; kind = "pre"; }
    else if (player && s5774_pl_left) { s5774_pl_left--; emit = 1; kind = "player"; }
    else if (!player && s5774_np_left) { s5774_np_left--; emit = 1; kind = "ctl"; }
    else if ((s5774_total % 4000u) == 0u && s5774_total <= 24000u) emit = 1;
    if (!emit) return;
    extern long long rs64_s5773_ms(void);
    extern unsigned long rs64_s5773_ord(void);
    fprintf(stderr, "[debris-call] ord=%lu t=%lld kind=%s site=0x%08X fn=%s a0=0x%08X a1=0x%08X player=%d hw=0x%04X n=%u c0=%u c1=%u c2=%u c3=%u c4=%u\\n",
        rs64_s5773_ord(), rs64_s5773_ms(), kind, site, fn, a0, (unsigned)U32(ctx->r5), player, hw, s5774_total,
        s5774_c[0], s5774_c[1], s5774_c[2], s5774_c[3], s5774_c[4]);
    fflush(stderr);
}
"""


def apply(text):
    if TAG in text:
        return text, 0
    lines = text.splitlines(keepends=True)
    jal_at = {}
    for i, line in enumerate(lines):
        if ": jal         0x800B01E4" not in line:
            continue
        parts = line.split()
        if len(parts) < 2 or not parts[1].endswith(":"):
            raise RuntimeError(f"unparsed jal line: {line!r}")
        pc = parts[1][:-1]
        if pc not in SITES:
            raise RuntimeError(f"unexpected jal pc {pc}")
        jal_at[i] = pc
    if len(jal_at) != 5:
        raise RuntimeError(f"jal count {len(jal_at)} != 5")
    inserts = {}
    for i, pc in jal_at.items():
        found = None
        for j in range(i + 1, min(i + 8, len(lines))):
            if "spawnSceneDebrisAndEffectCluster(rdram, ctx);" in lines[j]:
                found = j
                break
        if found is None:
            raise RuntimeError(f"no call within 8 lines of {pc}")
        if found in inserts:
            raise RuntimeError(f"two jals share call line {found}")
        inserts[found] = pc
    out = []
    helper_done = False
    n = 0
    for i, line in enumerate(lines):
        if not helper_done and line.startswith('#include "funcs.h"'):
            out.append(line)
            out.append(HELPER if HELPER.endswith("\n") else HELPER + "\n")
            helper_done = True
            continue
        if i in inserts:
            pc = inserts[i]
            idx, fn = SITES[pc]
            out.append(
                f'    s5774_debris_log(rdram, ctx, {pc}u, {idx}, "{fn}"); /* {TAG} */\n'
            )
            n += 1
        out.append(line)
    if not helper_done:
        raise RuntimeError('missing #include "funcs.h"')
    if n != 5:
        raise RuntimeError(f"inserted {n}")
    return "".join(out), n


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_30.c"
    updated, count = apply(p.read_text())
    if count:
        p.write_text(updated)
    print(f"{p}: s5774 debris caller x{count}")
