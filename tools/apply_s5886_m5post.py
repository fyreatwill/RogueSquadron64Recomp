"""s5886: slotDispatcherIter msg-5 post-side witness (ROGUESQ_LOG_HUDBIT). At the per-slot point (0x8003E944, s1=slot, s7=a1 msg) logs every msg==5
visit whose slot has an 0x803xxxxx descriptor at +0x34: caller ra (saved at sp+0x34), a0 selector, a2, desc, cls (+0x70), vi. Joins to
'[supply] destroy-ctx' on desc. Control: class-0 msg-5 lines must exist and class-0 destroys must join. Idempotent; mirrored into fixup."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s5886 m5 post"
ANC = "    // 0x8003E944: lbu         $v0, 0x1A($s1)\n"
HOOK = ('    { /* ' + TAG + ' */ static int s_e = -1; static unsigned s_n; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; }\n'
        '      if (s_e && (U32(ctx->r23) & 0xFFFFu) == 5u && U32(ctx->r17) >= 0x80000000u && U32(ctx->r17) < 0x80800000u && s_n++ < 400) {\n'
        '        extern volatile uint32_t rs64_vi_n_g; fprintf(stderr, "[m5post] slot=%08X upd=%08X d34=%08X d70=%08X sel=%08X a2=%08X entry_ra=%08X vi=%u n=%u\\n", U32(ctx->r17), (uint32_t)MEM_W(ctx->r17, 0), (uint32_t)MEM_W(ctx->r17, 0X34), (uint32_t)MEM_W(ctx->r17, 0X70), U32(ctx->r20), U32(ctx->r30), (uint32_t)MEM_W(ctx->r29, 0X34), rs64_vi_n_g, s_n); } }\n')
def apply(text):
    if "RECOMP_FUNC void slotDispatcherIter(" not in text or TAG in text: return text, 0
    i = text.find("RECOMP_FUNC void slotDispatcherIter(")
    j = text.find(ANC, i)
    assert 0 < j - i < 40000
    return text[:j] + HOOK + text[j:], 1
if __name__ == "__main__":
    p = base / "funcs_8.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("live patched x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5886_m5post" in s: print("fixup already")
    else:
        anc = '    if p.name == "funcs_36.c":\n        import apply_s5829_teardown_gate'
        assert s.count(anc) == 1
        blk = ('    if p.name == "funcs_8.c":\n        import apply_s5886_m5post as _a5886\n        text, _n5886 = _a5886.apply(text)\n'
               '        if _n5886:\n            changed = True\n            report.append(f"{p.name}: s5886 m5 post x{_n5886}")\n\n')
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5816_slot_expiry.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5886_m5post.py",\n', 1)
        fp.write_text(s); print("fixup patched")
