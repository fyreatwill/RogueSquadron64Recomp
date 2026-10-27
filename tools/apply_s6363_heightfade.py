"""s6363 G3c(a): terrain height-byte fade at renderFlatMeshFaceGroup 0x80011788.

The F5 ucode TRI_GEN builds terrain vertex y from 25 height bytes (s6362); the CPU hands
the pointer over via `lw v0,0x24(s0)` / `sw v0,8(a3)` at 0x80011788/8C. This hook copies the
25 bytes to a guest scratch ring (0x80FF0000.., below 16 MB so the RSP DMA can reach it),
edits them, and passes the scratch pointer instead.
Fade factor f comes from the radfade2 hook (last A6C0 radius fade, same frame) so the
colour env ROGUESQ_EDGE_FADE_R2=r0,r1,116,68 must also be set to enable the radius calc.
Env (opt-in, normal runs unchanged):
  ROGUESQ_EDGE_FADE_R2_Y=<hz>   lerp heights toward hz (0..255; -1 = cell mean) by f; also
                                suppresses the radfade2 colour tint so only geometry changes
  ROGUESQ_EDGE_FADE_R2_YC=<k>   positive control: add k to every height byte of every cell
  ROGUESQ_EDGE_FADE_R2_YLOG=1   log first 40 hook hits + 1/20011
"""
import pathlib

BASE = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s6363 heightfade"

HOOK = (
    '    { /* PATCH: s6363 heightfade */ extern float rs64_s6363_f; extern int rs64_s6363_y; static int en = -1, yc = 0, hz = 0, lg = 0; static unsigned n = 0, ring = 0;\n'
    '      if (en < 0) { en = 0; const char* e = getenv("ROGUESQ_EDGE_FADE_R2_Y"); const char* c = getenv("ROGUESQ_EDGE_FADE_R2_YC"); lg = getenv("ROGUESQ_EDGE_FADE_R2_YLOG") ? 1 : 0; if (e && *e) { hz = atoi(e); en |= 1; rs64_s6363_y = 1; } if (c && *c) { yc = atoi(c); en |= 2; } }\n'
    '      uint32_t sp6363 = U32(ctx->r2);\n'
    '      if (en && sp6363 >= 0x80000000u && sp6363 < 0x807FFFC0u) { uint32_t dst = 0x80FF0000u + (ring++ & 2047u) * 32u; int v[25]; int sum = 0;\n'
    '        for (int q = 0; q < 25; q++) { v[q] = (uint8_t)MEM_B(q, (int64_t)(int32_t)sp6363); sum += v[q]; }\n'
    '        double f = (en & 1) ? rs64_s6363_f : 0.0; int target = (hz < 0) ? sum / 25 : hz;\n'
    '        for (int q = 0; q < 25; q++) { double x = v[q] + (target - v[q]) * f + ((en & 2) ? yc : 0); if (x < 0) x = 0; if (x > 255) x = 255; MEM_B(q, (int64_t)(int32_t)dst) = (int8_t)(uint8_t)x; }\n'
    '        if (lg && (n < 40u || (n % 20011u) == 0u)) fprintf(stderr, "[heightfade] n=%u src=%08X f=%g tgt=%d v0=%d v12=%d v24=%d\\n", n, sp6363, f, target, v[0], v[12], v[24]);\n'
    '        n++; ctx->r2 = (gpr)(int32_t)dst; } }\n'
)
ANCHOR = "    // 0x80011788: lw          $v0, 0x24($s0)\n    ctx->r2 = MEM_W(ctx->r16, 0X24);\n"


def apply4(text):
    if MARK in text:
        return text, 0
    i = text.find(ANCHOR)
    if i < 0:
        return text, 0
    j = i + len(ANCHOR)
    return text[:j] + HOOK + text[j:], 1


def apply10(text):
    if "PATCH: s6363 fexport" in text:
        return text, 0
    old = "f = f * f * (3.0 - 2.0 * f);\n"
    i = text.find("PATCH: s6328 radfade2")
    if i < 0:
        return text, 0
    j = text.find(old, i)
    if j < 0 or j - i > 3000:
        return text, 0
    new = old[:-1] + " rs64_s6363_f = (float)f; /* PATCH: s6363 fexport */\n"
    k = text.find("RECOMP_FUNC", 0)
    defs = "float rs64_s6363_f = 0.0f; int rs64_s6363_y = 0; /* PATCH: s6363 fexport */\n"
    t = text[:j] + new + text[j + len(old):]
    # suppress the colour tint when the geometry arm owns the fade
    s = "if (en6328 && f > 0.0) for (int q = 0; q < 3; q++)"
    t = t.replace(s, "if (en6328 && f > 0.0 && !rs64_s6363_y) for (int q = 0; q < 3; q++)", 1)
    return t[:k] + defs + t[k:], 1


if __name__ == "__main__":
    p4 = BASE / "funcs_4.c"
    t, n = apply4(p4.read_text())
    if n:
        p4.write_text(t)
    p10 = BASE / "funcs_10.c"
    t, m = apply10(p10.read_text())
    if m:
        p10.write_text(t)
    print(f"s6363 heightfade patched funcs_4 x{n} funcs_10 x{m}")
