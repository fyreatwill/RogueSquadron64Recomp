"""s5806: ROGUESQ_NPC_INVULN=1 is a TEST-ONLY lever. At updateDestructionDebrisNpc ENTRY, for a msg-5 (HIT) on an NPC whose
descriptor +0x70 == 2 (counter-2 class, s5792-s5793), zero the hit record's damage halfword (a2+6) so descriptor hp is never
depleted and the objective-counter-2 tally (lv0 fail rule getObjectiveCount(2)>=3) cannot fire. Logs the first 20 zeroed hits
([npcinv]) as the positive control. Idempotent; mirrored into fixup_game_funcs_vendored.py."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5806 npc invuln"
ANC = "    ctx->r17 = MEM_W(ctx->r21, 0X4);\n"
B = ('    { static int s_i = -1; static unsigned s_in = 0; if (s_i < 0) { const char* e = getenv("ROGUESQ_NPC_INVULN"); s_i = (e && e[0] == \'1\') ? 1 : 0; } '
     'if (s_i && (unsigned)(ctx->r5 & 0xFFFF) == 5 && ((uint32_t)ctx->r6 >> 24) == 0x80 && ((uint32_t)ctx->r17 >> 24) == 0x80) { '
     'uint32_t d = (uint32_t)MEM_W(ctx->r17, 0X34); '
     'if (d >= 0x80300000u && d < 0x80330000u && (uint32_t)MEM_W(S32((int32_t)d), 0X70) == 2) { '
     'uint32_t dmg = (uint32_t)MEM_HU(ctx->r6, 0X6); MEM_H(0X6, ctx->r6) = 0; '
     'if (s_in++ < 20) fprintf(stderr, "[npcinv] npc=%08x desc=%08x dmg=%u->0 n=%u\\n", (uint32_t)ctx->r17, d, dmg, s_in); } } } /* ' + T + ' */\n')
def apply(text, name=None):
    n = 0
    i = text.find("RECOMP_FUNC void updateDestructionDebrisNpc(")
    if i >= 0 and T not in text:
        j = text.find(ANC, i)
        if j >= 0: k = j + len(ANC); text = text[:k] + B + text[k:]; n += 1
    return text, n
if __name__ == "__main__":
    p = base / "funcs_16.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_16.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5806_npc_invuln" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_16.c":\n'
               '        import apply_s5806_npc_invuln as _a5806\n'
               '        text, _n5806 = _a5806.apply(text)\n'
               '        if _n5806:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5806 npc invuln x{_n5806}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5793_npc_diff.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5806_npc_invuln.py",\n', 1)
        fp.write_text(s); print("fixup patched")
