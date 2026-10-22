"""s5880: TEST-ONLY lever ROGUESQ_NO_CRASH=1 - skip the player's lethal collision calls.

Sites (updatePlayerCraftPhysics, funcs_30.c): the spawnSceneDebrisAndEffectCluster jal at
0x800B2EC4 and the spawnNpcDestructionDebris jal at 0x800B2A58. Only skipped when the
object (s3 / r19) is the player 0x80137DBC; the logging hooks above them still fire.
"""
import pathlib
import sys

TAG = "PATCH: s5880 no crash"
SITES = (
    ("s5774_debris_log(rdram, ctx, 0x800B2EC4u", "spawnSceneDebrisAndEffectCluster(rdram, ctx);"),
    ("s5779_bit8_log(rdram, ctx, 0x800B2A58u", "spawnNpcDestructionDebris(rdram, ctx);"),
)
HELPER = """/* """ + TAG + """ */
static int s5880_e = -1;
static int s5880_skip(recomp_context* ctx) {
    if (s5880_e < 0) {
        const char* e = getenv("ROGUESQ_NO_CRASH");
        s5880_e = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    return s5880_e && (unsigned)U32(ctx->r19) == 0x80137DBCu;
}
"""


def apply(text):
    if TAG in text:
        return text, 0
    lines = text.splitlines(keepends=True)
    out = []
    helper_done = False
    n = 0
    pending = None
    for line in lines:
        if not helper_done and line.startswith('#include "funcs.h"'):
            out.append(line)
            out.append(HELPER)
            helper_done = True
            continue
        if pending and line.strip() == pending:
            out.append(f"    if (!s5880_skip(ctx)) {line.strip()} /* {TAG} */\n")
            pending = None
            n += 1
            continue
        out.append(line)
        for marker, call in SITES:
            if marker in line:
                pending = call
    if not helper_done:
        raise RuntimeError('missing #include "funcs.h"')
    if n != 2:
        raise RuntimeError(f"patched {n}")
    return "".join(out), n


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_30.c"
    updated, count = apply(p.read_text())
    if count:
        p.write_text(updated)
    print(f"{p}: s5880 no crash x{count}")
