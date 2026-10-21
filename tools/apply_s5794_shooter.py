"""s5794: under ROGUESQ_LOG_HUDBIT, at the projectile hit-send (MIPS 0x8005D35C, before jal 0x8003E8DC) log the first 3 hits per shooter id:
victim id (a0), projectile node words 0..31 + its desc (+0x34), shooter node (table 0x80130BB0 + id*8) words 0..31 + its desc words. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5794 shooter id"
ANC = "    // 0x8005D35C: jal         0x8003E8DC\n"
B = ('    { static int s_e = -1; static uint32_t s_id[16]; static int s_cnt[16], s_n = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
     'if (s_e) { uint32_t sid = (uint32_t)MEM_HU(ctx->r17, 0XF8); int k = -1; for (int i = 0; i < s_n; i++) if (s_id[i] == sid) k = i; if (k < 0 && s_n < 16) { k = s_n++; s_id[k] = sid; } '
     'if (k >= 0 && s_cnt[k] < 3) { s_cnt[k]++; uint32_t pn = U32(ctx->r17); uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0); uint32_t sn = (uint32_t)MEM_W(S32((int32_t)(tb + (sid & 0xFFFF) * 8)), 0); '
     'fprintf(stderr, "[shooter] n=%d sid=%04x victim=%04x dmg=%u proj=%08x shooter=%08x\\n  proj:", s_cnt[k], sid, (unsigned)(ctx->r4 & 0xFFFF), (unsigned)MEM_HU(ctx->r17, 0XFC), pn, sn); '
     'for (int q = 0; q < 32; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(S32((int32_t)pn), q * 4)); '
     'uint32_t pd = (uint32_t)MEM_W(S32((int32_t)pn), 0X34); fprintf(stderr, "\\n  projdesc=%08x:", pd); if (pd >= 0x80000000u && pd < 0x80400000u) for (int q = 0; q < 28; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(S32((int32_t)pd), q * 4)); '
     'if (sn >= 0x80000000u && sn < 0x80400000u) { fprintf(stderr, "\\n  shooter:"); for (int q = 0; q < 32; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(S32((int32_t)sn), q * 4)); '
     'uint32_t sd = (uint32_t)MEM_W(S32((int32_t)sn), 0X34); fprintf(stderr, "\\n  shooterdesc=%08x:", sd); if (sd >= 0x80000000u && sd < 0x80400000u) for (int q = 0; q < 28; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(S32((int32_t)sd), q * 4)); } else fprintf(stderr, "\\n  shooter node invalid/freed"); '
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
    if "apply_s5794_shooter" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_13.c":\n'
               '        import apply_s5794_shooter as _a5794\n'
               '        text, _n5794 = _a5794.apply(text)\n'
               '        if _n5794:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5794 shooter id x{_n5794}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5793_npc_diff.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5794_shooter.py",\n', 1)
        fp.write_text(s); print("fixup patched")
