"""s6418 G1c: the far-cutoff dist^2 float at 0x8009DEB4 (~14.5^2 = 210) is read by buildGridCellMeshForFace and severs the render chain
past it, independent of ROGUESQ_DRAW_DISTANCE (s6417 meshlog: chain == count(d2 < DEB4) in dd1/dd2/dd3 arms, list 336 -> 978 while chain stayed ~150).
Scale it by dd^2 at the s6036 hook (same in-flight gate and toggle as the DEAC window scale). ROGUESQ_DD_NOFARCLIP=1 disables (A/B). Idempotent.
Must run after apply_s6036_dd."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "c.u = ctx->f2.u32l; c.f *= me6036; ctx->f2.u32l = c.u; } }\n"
NEW = r'''c.u = ctx->f2.u32l; c.f *= me6036; ctx->f2.u32l = c.u; }
      { /* PATCH: s6418 farclip */ static uint32_t org6418 = 0; static int off6418 = -1;
        if (off6418 < 0) { const char* e = getenv("ROGUESQ_DD_NOFARCLIP"); off6418 = (e && *e && *e != '0') ? 1 : 0; }
        if (!org6418) org6418 = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8009DEB4);
        if (org6418 && !off6418) { union { uint32_t u; float f; } c; c.u = org6418; if (me6036 != 1.0f && MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0) c.f *= me6036 * me6036; MEM_W(0, (int64_t)(int32_t)0x8009DEB4) = (int32_t)c.u; } } }
'''
def apply9(text):
    if "PATCH: s6418 farclip" in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
