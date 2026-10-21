"""s5753: ROGUESQ_LOG_MTM=1 dumps the runInMissionFrame event table (0x8010B350) once and logs the pending-event
mask word 0x8010C9E0 whenever it changes (sampled at the post-dispatch label L_800FA858, once per frame). Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5753 mtm mask"
BLOCK = ('    { static int s_f = 0, s_d = 0; static uint32_t s_m = 0xDEADBEEFu; s_f++; if (getenv("ROGUESQ_LOG_MTM")) { '
         'if (!s_d) { s_d = 1; for (int i = 0; i < 40; i++) { int32_t ea = (int32_t)0x8010B350 + i * 8; unsigned id = MEM_BU(ea, 0); '
         'fprintf(stderr, "[mtm] TABLE[%d] id=%u fn=0x%X\\n", i, id, (unsigned)MEM_W(ea, 4)); if (id == 0xFF) break; } } '
         'uint32_t m = (uint32_t)MEM_W(ctx->r23, -0X3620); if (m != s_m) { fprintf(stderr, "[mtm] MASK frame=%d 0x%08X -> 0x%08X\\n", s_f, s_m, m); s_m = m; } } } /* ' + TAG + ' */\n')
def apply(text):
    if TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void runInMissionFrame(uint8_t* rdram")
    assert i >= 0
    a = "L_800FA858:\n"
    j = text.find(a, i); assert 0 < j - i < 40000
    k = j + len(a)
    return text[:k] + BLOCK + text[k:], 1
if __name__ == "__main__":
    p = base / "funcs_42.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live funcs_42 patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    f = fp.read_text()
    if TAG in f: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_42.c" and "PATCH: s5753 mtm mask" not in text:\n'
               '        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
               '        import apply_s5753_mtm_mask as _a5753\n'
               '        text, _n5753 = _a5753.apply(text)\n'
               '        if _n5753:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5753 mtm mask x{_n5753}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert f.count(anc) == 1
        f = f.replace(anc, blk + anc, 1)
        lst = '    "apply_s5750_mtm_bt.py",\n'
        assert f.count(lst) == 1
        f = f.replace(lst, lst + '    "apply_s5753_mtm_mask.py",\n', 1)
        fp.write_text(f); print("fixup patched")
