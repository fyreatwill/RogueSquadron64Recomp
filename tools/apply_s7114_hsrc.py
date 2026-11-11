#!/usr/bin/env python3
"""s7114 fps60-wall-lod: which height data does the camera y clamp read, and which does the eye cell's TriGen draw?

Static read (s7114):
  0x80067D90 (recompiled name wrapAngleToCyclicRange, a misnomer: it is the terrain height sampler the y clamp in
    applyPlayerVehicleStateUpdate calls at 0x8004CFDC): struct 0x80136DC0: +0 u16 tile map, +4 tile array (30-byte tiles,
    25 s8 heights at +5, 5x5 row-major, 0.5 u spacing), +0x10 height scale, +0x18 global y offset, +0x20/+0x2C x/z origins,
    +0x38/+0x3A map dims. Tile ptr a0 = *(+4) + (map[row*w + col] & 0x1FFF) * 30 (0x80067FD4); quarter indices t1 (x) / t0 (z),
    fractions f6 / f4; plane split on f6 - f4 >= 0 (bc1f 0x80067FD0); y = interp(s8) * (+0x10 * 0x8003C7EC) + *(+0x18).
  TriGen (renderFlatMeshFaceGroup height path L_80011714): w0 = 0x05 | elem+0x20<<16 | (elem+0x15&15)<<12 | (elem+0x2E&1)<<8 |
    lod(elem+0x10); params[1] = option bytes elem+0x11..0x14; params[2] = elem+0x24 (the 25-byte s8 height pointer, GLideN64
    TriGen0000_PrepareVtxData; lod 1 = TriGen0001 reads rows/cols 0,2,4 of the same 25 bytes); params[5..7] = ponderation shorts
    elem+0x16..0x1E; params[8] = elem+8 (x) | elem+0xA (y base, << 4 in the ucode); params[9] = elem+0xC (z) | elem+0x22 << lod.
Hooks (measurement only, gate ROGUESQ_S7114_HSRC=1 and the s7101 CHASE file open):
  funcs_16 sampler: entry clears g_s7114_tl; at 0x80067FD8 (plane A) and L_80068074 (plane B) records tl = a0, q = t1 | t0 << 4 |
    plane << 8, fx = f6, fz = f4.
  funcs_10 applyPlayerVehicleStateUpdate after the y-clamp call (after_10, where s7103 takes h): line
    hx m=<mach> tl=<tile ptr or 0> q=<qx>,<qz>,<plane> fr=<fx>,<fz> h=<sampler y> sc=<+0x10> y0=<+0x18> b=<25 bytes at tl+5, hex>
  funcs_4 s7105_visit, eye cell only (g_s7105_el[24], ring 0): line
    ht m=<mach> el=<elem> c=<10 cmd words> hb=<25 bytes at params[2], hex>
Positive control: hx tl must be nonzero on flight ticks and h must equal the bilinear-plane rebuild from b= with q/fr/sc/y0
(offline, exact to float rounding), and at least some ticks must have params[2] == tl + 5 (camera tile == eye cell) or the join
is not comparing the same cell. Idempotent; listed in fixup_game_funcs_vendored.py after apply_s7111_camfixk.py."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7114 hsrc"

G16 = ('/* ' + MARK + ' state */\nuint32_t g_s7114_tl, g_s7114_q; float g_s7114_fx, g_s7114_fz;\n')
FN16 = "RECOMP_FUNC void wrapAngleToCyclicRange(uint8_t* rdram, recomp_context* ctx) {\n"
E16 = [("    // 0x80067D90: lui         $v0, 0x8013\n",
        "    g_s7114_tl = 0; /* " + MARK + " */\n    // 0x80067D90: lui         $v0, 0x8013\n"),
       ("    // 0x80067FD8: sll         $v1, $t0, 2\n",
        "    g_s7114_tl = (uint32_t)ctx->r4; g_s7114_q = (uint32_t)(ctx->r9 & 15) | (uint32_t)(ctx->r8 & 15) << 4; g_s7114_fx = ctx->f6.fl; g_s7114_fz = ctx->f4.fl; /* " + MARK + " */\n"
        "    // 0x80067FD8: sll         $v1, $t0, 2\n"),
       ("L_80068074:\n    // 0x80068074: addiu       $v1, $t0, 0x1\n",
        "L_80068074:\n    g_s7114_tl = (uint32_t)ctx->r4; g_s7114_q = (uint32_t)(ctx->r9 & 15) | (uint32_t)(ctx->r8 & 15) << 4 | 0x100; g_s7114_fx = ctx->f6.fl; g_s7114_fz = ctx->f4.fl; /* " + MARK + " */\n"
        "    // 0x80068074: addiu       $v1, $t0, 0x1\n")]

FN10 = "RECOMP_FUNC void applyPlayerVehicleStateUpdate(uint8_t* rdram, recomp_context* ctx) {\n"
PRE10 = (
    '/* ' + MARK + ' externs */\n'
    'extern uint32_t g_s7114_tl, g_s7114_q; extern float g_s7114_fx, g_s7114_fz;\n'
    'int s7114_on(void) { static int on = -1; if (on < 0) { const char* e = getenv("ROGUESQ_S7114_HSRC"); on = (e && *e && *e != \'0\') ? 1 : 0; } return on; }\n'
    'static void s7114_bytes(uint8_t* rdram, FILE* f, uint32_t a) {\n'
    '  for (int i = 0; i < 25; i++) fprintf(f, "%02x", (a >= 0x80000000u && a < 0x83FFFFE0u) ? (unsigned)(uint8_t)MEM_B(i, (int64_t)(int32_t)a) : 0xEEu); }\n'
)
E10 = [("    s7103_h = ctx->f0.fl; /* PATCH: s7103 camfix */\n",
        "    s7103_h = ctx->f0.fl; /* PATCH: s7103 camfix */\n"
        "    if (s7101_cf && s7114_on() == 1) { int64_t sb = (int64_t)(int32_t)0x80136DC0u; uint32_t u1 = (uint32_t)MEM_W(0x10, sb), u2 = (uint32_t)MEM_W(0x18, sb); float sc, y0; memcpy(&sc, &u1, 4); memcpy(&y0, &u2, 4); /* " + MARK + " */\n"
        "      fprintf(s7101_cf, \"hx m=%llu tl=%08X q=%u,%u,%u fr=%.6g,%.6g h=%.7g sc=%.7g y0=%.7g b=\", s7102_m(), g_s7114_tl, g_s7114_q & 15, (g_s7114_q >> 4) & 15, g_s7114_q >> 8,\n"
        "        (double)g_s7114_fx, (double)g_s7114_fz, (double)ctx->f0.fl, (double)sc, (double)y0);\n"
        "      s7114_bytes(rdram, s7101_cf, g_s7114_tl ? g_s7114_tl + 5 : 0); fputc('\\n', s7101_cf); }\n")]

PRE4 = (
    '/* ' + MARK + ' eye-cell TriGen source */\n'
    'extern FILE* s7101_cf; extern int s7114_on(void);\n'
    'static void s7114_ht(uint8_t* rdram, uint32_t el, uint32_t cmd) { extern uint64_t mach_absolute_time(void); FILE* f = s7101_cf;\n'
    '  if (!f || s7114_on() != 1) return; fprintf(f, "ht m=%llu el=%08X c=", (unsigned long long)mach_absolute_time(), el);\n'
    '  for (int i = 0; i < 10; i++) fprintf(f, "%08x%c", (uint32_t)MEM_W(4 * i, (int64_t)(int32_t)cmd), i < 9 ? \',\' : \' \');\n'
    '  uint32_t a = (uint32_t)MEM_W(8, (int64_t)(int32_t)cmd); a = 0x80000000u | (a & 0x00FFFFFFu); fputs("hb=", f);\n'
    '  for (int i = 0; i < 25; i++) fprintf(f, "%02x", (unsigned)(uint8_t)MEM_B(i, (int64_t)(int32_t)a)); fputc(\'\\n\', f); }\n'
)
A4 = "g_s7105_w0[i] = (uint32_t)MEM_W(0, (int64_t)(int32_t)cmd);\n"
L4 = "g_s7105_w0[i] = (uint32_t)MEM_W(0, (int64_t)(int32_t)cmd);\n    if (i == 24 && !un) s7114_ht(rdram, el, cmd); /* " + MARK + " */\n"


def patch_fn(path, pre, fn, edits, pre_before=None):
    t = path.read_text(errors="surrogateescape")
    if MARK in t:
        print(path.name, "s7114 already applied"); return
    i = t.index(fn); j = t.index("\nRECOMP_FUNC ", i + len(fn)); body = t[i:j]
    for a, r in edits:
        n = body.count(a)
        if n != 1: sys.exit("s7114: %s anchor count %d for %r" % (path.name, n, a[:70]))
        body = body.replace(a, r)
    t = t[:i] + pre + body + t[j:]
    path.write_text(t, errors="surrogateescape"); print(path.name, "s7114 applied")


patch_fn(BASE / "funcs_16.c", G16, FN16, E16)
# funcs_10: helpers need s7101_cf / s7102_m declared before the function (s7102 PRE block)
p10 = BASE / "funcs_10.c"; t10 = p10.read_text(errors="surrogateescape")
if "PATCH: s7103 camfix" not in t10: sys.exit("s7114: needs apply_s7103_camfix first")
patch_fn(p10, PRE10, FN10, E10)
# funcs_4: extend the s7105 visit helper (PRE4 of apply_s7105_emit)
p4 = BASE / "funcs_4.c"; t4 = p4.read_text(errors="surrogateescape")
if MARK in t4: print("funcs_4.c s7114 already applied")
else:
    if t4.count(A4) != 1: sys.exit("s7114: funcs_4 s7105 visit anchor count %d" % t4.count(A4))
    k = t4.index("static inline void s7105_visit(")
    t4 = t4[:k] + PRE4 + t4[k:].replace(A4, L4, 1)
    p4.write_text(t4, errors="surrogateescape"); print("funcs_4.c s7114 applied")
