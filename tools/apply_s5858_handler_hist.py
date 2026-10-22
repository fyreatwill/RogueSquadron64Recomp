"""s5858: npcGroundTroopUpdate entry histogram by msg type (a1&0xFFFF), entries at L_800E84B8 (type-5 index 4 path),
hp<=0 at the 0x800E84C4 blez (via getNpcCurrentHealth result), and dealDamageToNpc calls made inside type-5 handler calls.
Under ROGUESQ_LOG_HITS=1. Positive control: total entries and type-1 (update tick) counts must be large."""
import pathlib
T = "PATCH: s5858 handler hist"
FN = "RECOMP_FUNC void npcGroundTroopUpdate("
NXT = "RECOMP_FUNC void playAttachmentCueNoTexture("
H = r"""/* PATCH: s5858 handler hist */
extern unsigned rs5858_dd; unsigned rs5858_ty[16], rs5858_l84b8, rs5858_hple0, rs5858_hpgt0, rs5858_dd5, rs5858_n; static int rs5858_en = -1;
"""
W = r"""RECOMP_FUNC void npcGroundTroopUpdate(uint8_t* rdram, recomp_context* ctx) { /* PATCH: s5858 handler hist */
    if (rs5858_en < 0) { const char* e = getenv("ROGUESQ_LOG_HITS"); rs5858_en = (e && e[0] == '1'); }
    if (!rs5858_en) { rs5858_inner(rdram, ctx); return; }
    unsigned ty = (unsigned)(ctx->r5 & 0xFFFF), d0 = rs5858_dd; rs5858_ty[ty < 15 ? ty : 15]++; rs5858_n++;
    rs5858_inner(rdram, ctx);
    if (ty == 5) rs5858_dd5 += rs5858_dd - d0;
    if ((rs5858_n & 4095) == 0 || (ty == 5 && (rs5858_ty[5] & 63) == 0)) {
        fprintf(stderr, "[s5858] n=%u ty:", rs5858_n); for (int i = 0; i < 16; i++) fprintf(stderr, " %u", rs5858_ty[i]);
        fprintf(stderr, " | L84B8=%u hp<=0=%u hp>0=%u dd_in_ty5=%u dd_total=%u\n", rs5858_l84b8, rs5858_hple0, rs5858_hpgt0, rs5858_dd5, rs5858_dd);
    }
}
"""
A1 = "L_800E84B8:\n"
A2 = "    after_68:\n    // 0x800E84C4: blez        $v0, L_800E85E8\n"
def apply(text, name=None):
    if T in text: return text, 0
    i = text.find(FN); j = text.find(NXT, i)
    if i < 0 or j < 0: return text, 0
    body = text[i:j]
    if body.count(A1) != 1 or body.count(A2) != 1: return text, 0
    body = body.replace(FN, "static void rs5858_inner(", 1)
    body = body.replace(A1, A1 + "    rs5858_l84b8++;\n", 1)
    body = body.replace(A2, "    after_68:\n    if (SIGNED(ctx->r2) <= 0) rs5858_hple0++; else rs5858_hpgt0++;\n    // 0x800E84C4: blez        $v0, L_800E85E8\n", 1)
    return text[:i] + H + body + W + text[j:], 1
def apply41(text, name=None):
    if "unsigned rs5858_dd;" in text: return text, 0
    a = "    n++; if (dmg) pos++;"
    if text.count(a) != 1: return text, 0
    text = text.replace(a, "    rs5858_dd++; " + a.lstrip(), 1)
    h = "/* PATCH: s5857 helpers */\n"
    return text.replace(h, "unsigned rs5858_dd;\n" + h, 1), 1
if __name__ == "__main__":
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    for f, fn in (("funcs_39.c", apply), ("funcs_41.c", apply41)):
        p = base / f; t = p.read_text(); t2, n = fn(t)
        if n: p.write_text(t2)
        print(f, n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5858_handler_hist" in s: print("fixup already")
    else:
        blk = ('    if p.name in ("funcs_39.c", "funcs_41.c"):\n'
               '        import apply_s5858_handler_hist as _a5858\n'
               '        text, _n5858 = (_a5858.apply if p.name == "funcs_39.c" else _a5858.apply41)(text)\n'
               '        if _n5858:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5858 handler hist x{_n5858}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5857_dmg_log.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5858_handler_hist.py",\n', 1)
        fp.write_text(s); print("fixup patched")
