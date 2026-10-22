"""s5857: log every dealDamageToNpc call (funcs_41.c): a0=npc stat obj, a1(r5)=damage, health before/after, +0x1A7 mode.
Under ROGUESQ_LOG_HITS=1. Prints first 60 calls + a per-4096-call... summary every 64 calls (calls, dmg>0, hp<=0 after, distinct objs).
Read-only wrapper: renames nothing, reads health through the same formula as getNpcCurrentHealth. Answers: does a type-5 SEND reach damage?"""
import pathlib
T = "PATCH: s5857 dmg log wrapper"
H = r"""/* PATCH: s5857 helpers */
static int rs5857_hp(uint8_t* rdram, uint32_t o) {
    if ((o >> 24) != 0x80) return -999999;
    uint32_t b = (uint32_t)MEM_W(S32((int32_t)o), 0x190);
    if (MEM_BU(S32((int32_t)o), 0x1A7)) return (int)b;
    if ((b >> 24) != 0x80) return -999998;
    return (int)MEM_W(S32((int32_t)b), 4 * (uint32_t)MEM_W(S32((int32_t)0x80137CE4u), 0));
}
"""
W = r"""RECOMP_FUNC void dealDamageToNpc(uint8_t* rdram, recomp_context* ctx) { /* PATCH: s5857 dmg log wrapper */
    static int en = -1; static unsigned n, pos, dead, no; static uint32_t objs[64];
    if (en < 0) { const char* e = getenv("ROGUESQ_LOG_HITS"); en = (e && e[0] == '1'); }
    uint32_t o = (uint32_t)ctx->r4, dmg = (uint32_t)ctx->r5; int pre = en ? rs5857_hp(rdram, o) : 0;
    rs5857_inner(rdram, ctx);
    if (!en) return;
    int post = rs5857_hp(rdram, o); unsigned z;
    for (z = 0; z < no; z++) if (objs[z] == o) break;
    if (z == no && no < 64) objs[no++] = o;
    n++; if (dmg) pos++; if (post <= 0) dead++;
    if (n <= 60) fprintf(stderr, "[s5857] dealDamage obj=%08x mode=%u dmg=%u hp %d->%d\n", o, (unsigned)MEM_BU(S32((int32_t)o), 0x1A7), dmg, pre, post);
    if ((n & 63) == 0) fprintf(stderr, "[s5857] calls=%u dmg>0=%u hp<=0=%u distinct_obj=%u\n", n, pos, dead, no);
}
"""
FN = "RECOMP_FUNC void dealDamageToNpc("
NXT = "RECOMP_FUNC void getNpcMissingHealth("
def apply(text, name=None):
    if T in text: return text, 0
    i = text.find(FN); j = text.find(NXT, i)
    if i < 0 or j < 0: return text, 0
    body = text[i:j].replace(FN, "static void rs5857_inner(", 1)
    return text[:i] + H + body + W + text[j:], 1
if __name__ == "__main__":
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_41.c"; t = p.read_text(); t2, n = apply(t)
    if n: p.write_text(t2)
    print("funcs_41.c x%d" % n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5857_dmg_log" in s: print("fixup already")
    else:
        blk = ('    if p.name == "funcs_41.c":\n'
               '        import apply_s5857_dmg_log as _a5857\n'
               '        text, _n5857 = _a5857.apply(text)\n'
               '        if _n5857:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5857 dmg log x{_n5857}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5838_send_effect.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5857_dmg_log.py",\n', 1)
        fp.write_text(s); print("fixup patched")
