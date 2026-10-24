"""s6061 G1c: log when allocateAndInitCraftNpcContext's rs_malloc(0x1E4) returns NULL (0x8006BD44 call site).
s6060 px4_dd2 SIGBUS is `sw $v0,0x80($s1)` at 0x8006BD80 with s1 = that unchecked malloc result (x10=0x80000080 => s1==0).
Diagnostic only: confirms guest-heap exhaustion as the mechanism. Idempotent; unset env = silent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    rs_malloc(rdram, ctx);\n        goto after_0;\n    // 0x8006BD48: sw          $s1, 0x14($sp)\n"
NEW = "    rs_malloc(rdram, ctx);\n    if ((uint32_t)ctx->r2 == 0u) { static int _n6061; if (_n6061++ < 8) fprintf(stderr, \"[mallocnull] allocateAndInitCraftNpcContext rs_malloc(0x1E4)==NULL a0cls=0x%X\\n\", (unsigned)(ctx->r16 & 0xF)); } /* PATCH: s6061 mallocnull */\n        goto after_0;\n    // 0x8006BD48: sw          $s1, 0x14($sp)\n"
def apply16(text):
    if "PATCH: s6061 mallocnull" in text or text.count(OLD) != 1: return text, 0
    return text.replace(OLD, NEW), 1
if __name__ == "__main__":
    p = base / "funcs_16.c"; t = p.read_text(); t2, n = apply16(t)
    if n: p.write_text(t2)
    print("funcs_16.c live patched x%d" % n)
