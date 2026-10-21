"""s5792: under ROGUESQ_LOG_HUDBIT log (a) at updateDestructionDebrisNpc's datItemSetObjectiveBooleanCount call site the NPC (s1) raw words +0..+0x5C and
descriptor words, (b) every dealDamagetoDatItem entry (a0..a3, ra). Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T1 = "PATCH: s5792 npc victim"; T2 = "PATCH: s5792 dmg entry"
A1 = "    datItemSetObjectiveBooleanCount(rdram, ctx);\n        goto after_53;\n"
B1 = ('    { static int s_e = -1, s_b = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
      'if (s_e && s_b < 24) { s_b++; struct { long s; int us; } tv; extern int gettimeofday(void*, void*); gettimeofday(&tv, 0); uint32_t n = U32(ctx->r17), d = MEM_W(ctx->r17, 0X34); fprintf(stderr, "[npcv] npc=%08x desc=%08x a2=%u parent=%08x t=%.0fms npc:", n, d, (unsigned)ctx->r6, (unsigned)ctx->r21, (double)(tv.s % 100000) * 1000.0 + tv.us / 1000.0); '
      'for (int q = 0; q < 24; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(ctx->r17, q * 4)); fprintf(stderr, " | desc:"); '
      'for (int q = 0; q < 40; q++) fprintf(stderr, " %08x", (unsigned)MEM_W(S32((int32_t)d), q * 4)); fprintf(stderr, "\\n"); } } /* ' + T1 + ' */\n')
FN2 = "RECOMP_FUNC void dealDamagetoDatItem("
ANC2 = "    int c1cs = 0;\n"
B2 = ('    { static int s_e = -1, s_b = 0; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
      'if (s_e && s_b < 80) { s_b++; fprintf(stderr, "[dmg] a0=%08x a1=%08x a2=%08x a3=%08x ra=%08x\\n", (unsigned)ctx->r4, (unsigned)ctx->r5, (unsigned)ctx->r6, (unsigned)ctx->r7, (unsigned)ctx->r31); } } /* ' + T2 + ' */\n')
def apply(text, name=None):
    n = 0
    i = text.find("RECOMP_FUNC void updateDestructionDebrisNpc(")
    if i >= 0 and T1 not in text:
        j = text.find("    datItemSetObjectiveBooleanCount(rdram, ctx);\n", i)
        if j >= 0: text = text[:j] + B1 + text[j:]; n += 1
    i = text.find(FN2)
    if i >= 0 and T2 not in text:
        j = text.find(ANC2, i)
        if j >= 0: k = j + len(ANC2); text = text[:k] + B2 + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    for f in ("funcs_16.c", "funcs_35.c"):
        p = base / f; t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        print(f, "x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5792_npc_victim" in s: print("fixup already")
    else:
        blk = ('    if p.name in ("funcs_16.c", "funcs_35.c"):\n'
               '        import apply_s5792_npc_victim as _a5792\n'
               '        text, _n5792 = _a5792.apply(text)\n'
               '        if _n5792:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5792 npc victim x{_n5792}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5791_objwr_bt.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5792_npc_victim.py",\n', 1)
        fp.write_text(s); print("fixup patched")
