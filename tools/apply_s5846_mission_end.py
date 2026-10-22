"""s5846: why does the mission end? Entry logs for beginMissionEndTransition (0x800FAF0C), tickMissionPhaseTransitionTimer (0x800FBBA8),
endMissionCleanup (0x800FB9E4). Under ROGUESQ_LOG_HUDBIT:
 [mend] fn=<name> n=<k> ra=.. flags(8010CA1C)=.. phase(8010CA20)=.. w1/w2 = next two words, vi=..
Tick fn logs only when (flags,phase) changed since its last log. Positive control: endMissionCleanup MUST log (the mission ends in every hold)."""
H = r'''/* PATCH: s5846 helpers */
extern volatile uint32_t rs64_vi_n_g;
static void rs5846_log(uint8_t* rdram, const char* fn, uint32_t ra, int chg) {
    static int e = -1; static unsigned n[5]; static uint32_t lf = 0xFFFFFFFFu, lp = 0xFFFFFFFFu;
    if (e < 0) { const char* v = getenv("ROGUESQ_LOG_HUDBIT"); e = (v && v[0]) ? 1 : 0; } if (!e) return;
    uint32_t f = (uint32_t)MEM_W((int32_t)0x8010CA1C, 0), p = (uint32_t)MEM_W((int32_t)0x8010CA20, 0);
    int k = fn[0] == 'b' ? 0 : fn[0] == 't' ? 1 : fn[0] == 'e' ? 2 : fn[0] == 'c' ? 3 : 4;
    if (chg) { if (f == lf && p == lp) return; lf = f; lp = p; }
    if (++n[k] > 40) return;
    fprintf(stderr, "[mend] fn=%s n=%u ra=%08X flags=%08X phase=%08X w1=%08X w2=%08X vi=%u\n", fn, n[k], ra, f, p,
        (uint32_t)MEM_W((int32_t)0x8010CA24, 0), (uint32_t)MEM_W((int32_t)0x8010CA28, 0), rs64_vi_n_g);
    if (k >= 2 && n[k] <= 3) { extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); void* bt[16]; int nb = backtrace(bt, 16); fprintf(stderr, "[mend-bt] %s\\n", fn); backtrace_symbols_fd(bt, nb, 2); } }
'''
FUNCS = [("beginMissionEndTransition", "0x800FAF0C: addiu       $sp, $sp, -0x18", 0),
         ("tickMissionPhaseTransitionTimer", "0x800FBBA8: addiu       $sp, $sp, -0x28", 1),
         ("clearMissionObjectiveFlagsAndEnterPhaseSix", "0x800FBD48: addiu       $sp, $sp, -0x18", 0),
         ("requestMissionTransitionMode", "0x800FB190: addiu       $sp, $sp, -0x20", 0),
         ("endMissionCleanup", "0x800FB9E4: addiu       $sp, $sp, -0x18", 0)]
def apply(text):
    n = 0
    if "RECOMP_FUNC void endMissionCleanup(" not in text: return text, 0
    if "PATCH: s5846 helpers" not in text:
        i = text.find("RECOMP_FUNC void beginMissionEndTransition("); text = text[:i] + H + text[i:]; n += 1
    for name, anchor, chg in FUNCS:
        tag = "PATCH: s5846 " + name
        if tag in text: continue
        i = text.find("RECOMP_FUNC void %s(" % name); A = "    // " + anchor + "\n"; j = text.find(A, i); assert j > 0 and j - i < 8000, name
        text = text[:j] + '    { /* %s */ rs5846_log(rdram, "%s", (uint32_t)ctx->r31, %d); }\n' % (tag, name, chg) + text[j:]; n += 1
    return text, n
