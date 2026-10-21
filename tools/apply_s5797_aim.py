"""s5797: under ROGUESQ_LOG_HUDBIT, at projectile creation (MIPS 0x8005CB10, in funcs_13.c) log the spawn record (s0): dir words 0..2, speed +0x10,
origin vec *(+0xC), owner +0x18, shooter node pos (+0xC0..C8 via table 0x80130BB0) and player slot0 node (0x80137DBC) pos, plus cosine(dir, player-origin)
and cosine(dir, shooter-forward-less). First 4 per owner id, 24 owners. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5797 aim"
ANC = "    // 0x8005CB10: sh          $v0, 0xF8($s1)\n"
B = ('    { static int s_e = -1; static uint32_t s_id[24]; static int s_cnt[24], s_n = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
     'if (s_e) { uint32_t rec = (uint32_t)ctx->r16; uint32_t sid = (uint32_t)MEM_HU(S32((int32_t)rec), 0X18); int k = -1; for (int i = 0; i < s_n; i++) if (s_id[i] == sid) k = i; if (k < 0 && s_n < 24) { k = s_n++; s_id[k] = sid; } '
     'if (k >= 0 && s_cnt[k] < 4 && rec >= 0x80000000u && rec < 0x80400000u) { s_cnt[k]++; '
     'float d[3], o[3], sp[3], pp[3], spd; uint32_t w; '
     'for (int q = 0; q < 3; q++) { w = (uint32_t)MEM_W(S32((int32_t)rec), q * 4); memcpy(&d[q], &w, 4); } w = (uint32_t)MEM_W(S32((int32_t)rec), 0x10); memcpy(&spd, &w, 4); '
     'uint32_t ov = (uint32_t)MEM_W(S32((int32_t)rec), 0xC); for (int q = 0; q < 3; q++) { w = (ov >= 0x80000000u && ov < 0x80400000u) ? (uint32_t)MEM_W(S32((int32_t)ov), q * 4) : 0u; memcpy(&o[q], &w, 4); } '
     'uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0); uint32_t sn = (uint32_t)MEM_W(S32((int32_t)(tb + (sid & 0xFFFF) * 8)), 0); '
     'for (int q = 0; q < 3; q++) { w = (sn >= 0x80000000u && sn < 0x80400000u) ? (uint32_t)MEM_W(S32((int32_t)sn), 0xC0 + q * 4) : 0u; memcpy(&sp[q], &w, 4); } '
     'for (int q = 0; q < 3; q++) { w = (uint32_t)MEM_W(S32((int32_t)0x80137DBCu), 0xC0 + q * 4); memcpy(&pp[q], &w, 4); } '
     'float v[3] = { pp[0] - o[0], pp[1] - o[1], pp[2] - o[2] }; float vn = sqrtf(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]), dn = sqrtf(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]); '
     'float cs = (vn > 1e-6f && dn > 1e-6f) ? (d[0]*v[0] + d[1]*v[1] + d[2]*v[2]) / (vn * dn) : 9.f; '
     'fprintf(stderr, "[aim] n=%d sid=%04x rec=%08x shooter=%08x vt=%08x dir=(%.3f %.3f %.3f) |d|=%.3f spd=%.2f org=(%.2f %.2f %.2f) shpos=(%.2f %.2f %.2f) plpos=(%.2f %.2f %.2f) dist_pl=%.1f cos_dir_to_player=%.3f\\n", '
     's_cnt[k], sid, rec, sn, (sn >= 0x80000000u && sn < 0x80400000u) ? (unsigned)MEM_W(S32((int32_t)sn), 0) : 0u, d[0], d[1], d[2], dn, spd, o[0], o[1], o[2], sp[0], sp[1], sp[2], pp[0], pp[1], pp[2], vn, cs); } } } /* ' + T + ' */\n')
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
    if "apply_s5797_aim" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_13.c":\n'
               '        import apply_s5797_aim as _a5797\n'
               '        text, _n5797 = _a5797.apply(text)\n'
               '        if _n5797:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5797 aim x{_n5797}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5794_shooter.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5797_aim.py",\n', 1)
        fp.write_text(s); print("fixup patched")
