"""s5779: which direct jal calls spawnNpcDestructionDebris before bit 0x8.

ROM census (rogue_squadron.z64): jal encoding 0x0C02C214 occurs twice, at
file offsets 0xB206C and 0xB3658. Their delta 0x15EC equals
0x800B2A58-0x800B146C, so those are the two VRAM sites. Zero j encodings
(0x0802C214) and zero raw 0x800B0850 pointers. The recompiled tree has the
same two calls and no other spawnNpcDestructionDebris() call.

The log is after the delay-slot a0 assignment and before the call, so it
precedes the in-callee [killset] store at 0x800B08DC. Gated by
ROGUESQ_LOG_MTM. Shares rs64_s5773_ord/ms with [lives].
"""
import pathlib
import sys

TAG = "PATCH: s5779 bit8 caller"

SITES = {
    "0x800B146C": (0, "tickCinematicObjectStateMachine"),
    "0x800B2A58": (1, "updatePlayerCraftPhysics"),
}

HELPER = """/* """ + TAG + """ */
static unsigned s5779_c[2];
static unsigned s5779_total;
static int s5779_e = -1;
static unsigned s5779_hw1_left = 40;
static unsigned s5779_pre_left = 16;
static unsigned s5779_pl_left = 12;
static unsigned s5779_np_left = 8;
static void s5779_bit8_log(uint8_t* rdram, recomp_context* ctx, unsigned site, int idx, const char* fn) {
    (void)rdram;
    if (s5779_e < 0) {
        const char* e = getenv("ROGUESQ_LOG_MTM");
        s5779_e = (e && e[0]) ? 1 : 0;
    }
    if (!s5779_e || idx < 0 || idx > 1) return;
    unsigned a0 = (unsigned)U32(ctx->r4);
    unsigned hw = (unsigned)MEM_HU(ctx->r4, 0x180);
    int player = (a0 == 0x80137DBCu);
    s5779_c[idx]++;
    s5779_total++;
    int emit = 0;
    if (player && hw == 0x0001u && s5779_hw1_left) { s5779_hw1_left--; emit = 1; }
    else if (player && (hw & 0x8u) == 0u && s5779_pre_left) { s5779_pre_left--; emit = 1; }
    else if (player && s5779_pl_left) { s5779_pl_left--; emit = 1; }
    else if (!player && s5779_np_left) { s5779_np_left--; emit = 1; }
    else if ((s5779_total % 2000u) == 0u && s5779_total <= 60000u) emit = 1;
    if (!emit) return;
    extern long long rs64_s5773_ms(void);
    extern unsigned long rs64_s5773_ord(void);
    fprintf(stderr, "[bit8call] ord=%lu t=%lld site=0x%08X fn=%s a0=0x%08X hw=0x%04X n=%u c0=%u c1=%u\\n",
        rs64_s5773_ord(), rs64_s5773_ms(), site, fn, a0, hw, s5779_total, s5779_c[0], s5779_c[1]);
    fflush(stderr);
}
"""


def apply(text):
    if TAG in text:
        return text, 0
    lines = text.splitlines(keepends=True)
    jal_at = {}
    for i, line in enumerate(lines):
        if ": jal         0x800B0850" not in line:
            continue
        parts = line.split()
        if len(parts) < 2 or not parts[1].endswith(":"):
            raise RuntimeError(f"unparsed jal line: {line!r}")
        pc = parts[1][:-1]
        if pc not in SITES:
            raise RuntimeError(f"unexpected jal pc {pc}")
        jal_at[i] = pc
    if len(jal_at) != 2:
        raise RuntimeError(f"jal count {len(jal_at)} != 2")
    inserts = {}
    for i, pc in jal_at.items():
        found = None
        for j in range(i + 1, min(i + 8, len(lines))):
            if "spawnNpcDestructionDebris(rdram, ctx);" in lines[j]:
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
                f'    s5779_bit8_log(rdram, ctx, {pc}u, {idx}, "{fn}"); /* {TAG} */\n'
            )
            n += 1
        out.append(line)
    if not helper_done:
        raise RuntimeError('missing #include "funcs.h"')
    if n != 2:
        raise RuntimeError(f"inserted {n}")
    return "".join(out), n


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_30.c"
    updated, count = apply(p.read_text())
    if count:
        p.write_text(updated)
    print(f"{p}: s5779 bit8 caller x{count}")
