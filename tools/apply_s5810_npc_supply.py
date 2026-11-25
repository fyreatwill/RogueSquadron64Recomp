"""s5810: under ROGUESQ_LOG_HUDBIT, in updateDestructionDebrisNpc (a) at NPC init (msg 1, sw s0,0x34(s1) @0x8006CC24) tally spawns by descriptor
+0x70 (class) and log every spawn whose +0x70==1 or +0x80==1 (desc, +0x70/74/78/7C/80/84, running sum of +0x74 for class 1); (b) at the objective-setter
call site tally destroy arrivals by the same key. Separates H-supply (spawned class-1 sum ~8) from H-port-skip (spawned sum >=21, destroy arrivals <spawns).
Idempotent; mirrored into fixup_game_funcs_vendored.py.
s7920: the s5885 destroy-ctx backtrace sat OUTSIDE the s_e gate (brace bug), so the first 8 destroy-ctx arrivals in normal play
ran backtrace()+backtrace_symbols_fd on the game thread; it is now under `if (s_e)`."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T0 = "PATCH: s5885 entry msg"; T1 = "PATCH: s5810 npc spawn tally"; T2 = "PATCH: s5810 npc destroy tally"
A1 = "RS64_S5798_ST(0x8006CC24u, 0X34, ctx->r17, 4); }\n"
A2 = "    datItemSetObjectiveBooleanCount(rdram, ctx);\n        goto after_53;\n"
T3 = "PATCH: s5885 destroy ctx"
B3 = '    { static int s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } uint32_t d = (uint32_t)MEM_W(ctx->r17, 0X34); if (s_e && d >= 0x80300000u && d < 0x80330000u) fprintf(stderr, "[supply] destroy-ctx desc=%08x +70=%u msg=%u entry_ra=%08x vi=%u\\n", d, (unsigned)MEM_W(S32((int32_t)d), 0X70), rs5885_msg, rs5885_ra, (unsigned)rs64_vi_n_g); if (s_e) { static unsigned s_bn; if (s_bn++ < 8) { void* bt[24]; int nb = backtrace(bt, 24); backtrace_symbols_fd(bt, nb, 2); } } } /* ' + T3 + ' */\n'
A0 = "    ctx->r3 = ADD32(ctx->r5, -0X1);\n"
B0 = "    { rs5885_msg = (uint32_t)ctx->r5 & 0xFFFFu; rs5885_ra = (uint32_t)ctx->r31; } /* " + T0 + " */\n"
PRE = '    { static int s_e = -1; if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_HUDBIT"); s_e = (e && e[0]) ? 1 : 0; } '
B1 = (PRE + 'static unsigned sp[8], sum1, sum80, tot, nl; uint32_t d = (uint32_t)ctx->r16; if (s_e && d >= 0x80300000u && d < 0x80330000u) { '
      'uint32_t c = (uint32_t)MEM_W(S32((int32_t)d), 0X70), c2 = (uint32_t)MEM_W(S32((int32_t)d), 0X80); tot++; sp[c < 7 ? c : 7]++; '
      'if (c == 1) sum1 += (uint32_t)MEM_W(S32((int32_t)d), 0X74); if (c2 == 1) sum80++; '
      'if ((c == 1 || c2 == 1) && nl < 200) { nl++; fprintf(stderr, "[supply] spawn npc=%08x desc=%08x +70=%u +74=%d +78=%08x +7C=%u +80=%u +84=%d | tot=%u cls0..7=%u,%u,%u,%u,%u,%u,%u,%u sum74(cls1)=%u n80eq1=%u\\n", '
      '(unsigned)ctx->r17, d, c, (int)MEM_W(S32((int32_t)d), 0X74), (unsigned)MEM_W(S32((int32_t)d), 0X78), (unsigned)MEM_W(S32((int32_t)d), 0X7C), c2, (int)MEM_W(S32((int32_t)d), 0X84), tot, sp[0], sp[1], sp[2], sp[3], sp[4], sp[5], sp[6], sp[7], sum1, sum80); } '
      'else if (tot % 25 == 0) fprintf(stderr, "[supply] tally tot=%u cls0..7=%u,%u,%u,%u,%u,%u,%u,%u sum74(cls1)=%u n80eq1=%u\\n", tot, sp[0], sp[1], sp[2], sp[3], sp[4], sp[5], sp[6], sp[7], sum1, sum80); } } /* ' + T1 + ' */\n')
B2 = (PRE + 'static unsigned dp[8], dsum1, dn; uint32_t d = (uint32_t)MEM_W(ctx->r17, 0X34); if (s_e && d >= 0x80300000u && d < 0x80330000u) { '
      'uint32_t c = (uint32_t)MEM_W(S32((int32_t)d), 0X70); dn++; dp[c < 7 ? c : 7]++; if (c == 1) dsum1 += (uint32_t)MEM_W(S32((int32_t)d), 0X74); '
      'fprintf(stderr, "[supply] destroy #%u desc=%08x +70=%u +74=%d +80=%u | cls0..7=%u,%u,%u,%u,%u,%u,%u,%u dsum74(cls1)=%u b39=%u\\n", dn, d, c, (int)MEM_W(S32((int32_t)d), 0X74), (unsigned)MEM_W(S32((int32_t)d), 0X80), '
      'dp[0], dp[1], dp[2], dp[3], dp[4], dp[5], dp[6], dp[7], dsum1, (unsigned)MEM_BU(0, S32((int32_t)0x80130B39))); } } /* ' + T2 + ' */\n')
def apply(text, name=None):
    n = 0
    i = text.find("RECOMP_FUNC void updateDestructionDebrisNpc(")
    if i < 0: return text, 0
    if T0 not in text:
        j = text.find(A0, i)
        if j >= 0:
            text = text[:i] + "#include <execinfo.h>\nextern volatile uint32_t rs64_vi_n_g; static uint32_t rs5885_msg, rs5885_ra;\n" + text[i:]
            j = text.find(A0, i); k = j + len(A0); text = text[:k] + B0 + text[k:]; n += 1
    if T1 not in text:
        j = text.find(A1, i)
        if j >= 0: k = j + len(A1); text = text[:k] + B1 + text[k:]; n += 1
    if T2 not in text:
        j = text.find(A2, i)
        if j >= 0: text = text[:j] + B2 + text[j:]; n += 1
    if T3 not in text:
        j = text.find(T2, i)
        if j >= 0:
            k = text.find("\n", j) + 1; text = text[:k] + B3 + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_16.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_16 x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5810_npc_supply" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_16.c":\n'
               '        import apply_s5810_npc_supply as _a5810\n'
               '        text, _n5810 = _a5810.apply(text)\n'
               '        if _n5810:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5810 npc supply x{_n5810}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5809_ctr1_log.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5810_npc_supply.py",\n', 1)
        fp.write_text(s); print("fixup patched")
