"""s5796: under ROGUESQ_LOG_HUDBIT, at the projectile hit-send (MIPS 0x8005D35C) log, once per victim id (16 max): victim node words 0..31 (table 0x80130BB0 + id*8),
and the halfword globals 0x80139550..0x801395A0 (slot-type words incl. 0x8013957C/0x80139562/0x8013959C). Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5796 victim node"
ANC = "    // 0x8005D35C: jal         0x8003E8DC\n"
B = ('    { static int s_e = -1; static uint32_t s_id[16]; static int s_n = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
     'if (s_e) { uint32_t vid = (uint32_t)(ctx->r4 & 0xFFFF); int k = -1; for (int i = 0; i < s_n; i++) if (s_id[i] == vid) k = i; if (k < 0 && s_n < 16) { s_id[s_n++] = vid; '
     'uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0); uint32_t vn = (uint32_t)MEM_W(S32((int32_t)(tb + vid * 8)), 0); '
     'fprintf(stderr, "[victim] id=%04x node=%08x sid=%04x glob:", vid, vn, (unsigned)MEM_HU(ctx->r17, 0XF8)); '
     'for (int q = 0; q < 40; q++) fprintf(stderr, " %04x", (unsigned)MEM_HU(S32((int32_t)0x80139550u), q * 2)); '
     'if (vn >= 0x80000000u && vn < 0x80400000u) { fprintf(stderr, "\\n  vnode:"); for (int q = 0; q < 32; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(S32((int32_t)vn), q * 4)); '
     'uint32_t vd = (uint32_t)MEM_W(S32((int32_t)vn), 0X34); fprintf(stderr, "\\n  vdesc=%08x:", vd); if (vd >= 0x80000000u && vd < 0x80400000u) for (int q = 0; q < 28; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(S32((int32_t)vd), q * 4)); } '
     'fprintf(stderr, "\\n"); } } } /* ' + T + ' */\n')
def apply(text, name=None):
    n = 0
    if T not in text and text.count(ANC) == 1:
        text = text.replace(ANC, B + ANC, 1); n = 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_13.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_13.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5796_victim" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_13.c":\n'
               '        import apply_s5796_victim as _a5796\n'
               '        text, _n5796 = _a5796.apply(text)\n'
               '        if _n5796:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5796 victim node x{_n5796}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5794_shooter.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5796_victim.py",\n', 1)
        fp.write_text(s); print("fixup patched")
