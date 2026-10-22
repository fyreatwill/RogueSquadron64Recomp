"""s5849: periodic [m47c] line at lv0_checkComplexObjectives entry (every 120 calls, plus first 3) logging objective counters
get(1), get(2), get(10) (0x8013805C+4n) and vi, under ROGUESQ_LOG_HUDBIT. Lets an invuln run show whether c1/c10 climb toward the win arm."""
T = "PATCH: s5849 cnt log"
B = ('    { static int n_ = 0, e_ = -1; if (e_ < 0) { const char* v_ = getenv("ROGUESQ_LOG_HUDBIT"); e_ = (v_ && v_[0]) ? 1 : 0; } '
     'if (e_ && (n_++ < 3 || n_ % 120 == 0)) { extern volatile uint32_t rs64_vi_n_g; fprintf(stderr, "[m47c] n=%d c1=%d c2=%d c10=%d vi=%u\\n", n_, '
     '(int)MEM_W((int32_t)0x8013805C + 4, 0), (int)MEM_W((int32_t)0x8013805C + 8, 0), (int)MEM_W((int32_t)0x8013805C + 40, 0), rs64_vi_n_g); } } /* ' + T + ' */\n')
def apply(text):
    i = text.find("RECOMP_FUNC void lv0_checkComplexObjectives(")
    if i < 0 or T in text: return text, 0
    a = "    int c1cs = 0;\n"; j = text.find(a, i); assert 0 < j - i < 400
    j += len(a); return text[:j] + B + text[j:], 1
if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        t = open(f).read(); t2, k = apply(t)
        if k: open(f, "w").write(t2)
        print(f, k)
