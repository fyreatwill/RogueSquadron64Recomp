"""M5 Step 9e: re-scan command-list record buffers after the audio task returns.

Diagnostic only (ROGUESQ_LOG_M5_CMDLIST / ROGUESQ_LOG_ALL). Extends the s4205 helper: every
record pointer seen at render return is pushed on a ring; rs64_s4207_after_audtask(), called
from librecomp rsp.cpp right after ucode_func(), counts for the records of that task how many
have a nonzero first 0x100 bytes at +0x7C (output) vs +0x2C (source, positive control).
"""
from pathlib import Path

MARK = "PATCH: s4207 postaud"
OLD = "    if (n <= 3 || (n % 512ul) == 0) {\n        fprintf(stderr, \"[m5-cmdlist]"
PUSH = ("    { /* PATCH: s4207 postaud push */ if (rec >= 0x80000000u && rec < 0x807FFF78u && "
        "rs64_s4207_n < 8192u) rs64_s4207_ring[rs64_s4207_n++] = rec; }\n")
HELPER = r'''
/* PATCH: s4207 postaud */
uint32_t rs64_s4207_ring[8192];
uint32_t rs64_s4207_n;
void rs64_s4207_after_audtask(uint8_t* rdram, int exit_reason) {
    static int enabled = -1;
    static uint32_t phase_key = 0xFFFFFFFFu;
    static unsigned long tasks, recs, out_nz, src_nz, out_ptr_ok, empty_tasks;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_CMDLIST");
        const char* a = getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') || (a && a[0] && a[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_phase_ord(void);
    uint32_t phase = rs64_phase_ord();
    if (phase != phase_key) { phase_key = phase; tasks = recs = out_nz = src_nz = out_ptr_ok = empty_tasks = 0; }
    ++tasks;
    uint32_t cnt = rs64_s4207_n, tout = 0, tsrc = 0;
    if (!cnt) ++empty_tasks;
    for (uint32_t k = 0; k < cnt; ++k) {
        gpr r = (gpr)(int32_t)rs64_s4207_ring[k];
        static const unsigned offs[2] = {0x7C, 0x2C};
        for (unsigned o = 0; o < 2; ++o) {
            uint32_t p = (uint32_t)MEM_W(offs[o], r);
            if (p >= 0x80000000u && p < 0x807FFF00u) {
                if (o == 0) ++out_ptr_ok;
                unsigned bz = 0;
                for (unsigned j = 0; j < 0x100; ++j) if (MEM_BU(j, (gpr)(int32_t)p)) ++bz;
                if (bz) { if (o == 0) ++tout; else ++tsrc; }
            }
        }
    }
    recs += cnt; out_nz += tout; src_nz += tsrc;
    rs64_s4207_n = 0;
    if (tasks <= 3 || (tasks % 128ul) == 0)
        fprintf(stderr, "[m5-postaud] phase=%u tasks=%lu exit=%d task_recs=%u task_out_nz=%u task_src_nz=%u cum_recs=%lu cum_out_nz=%lu cum_src_nz=%lu out_ptr_ok=%lu empty_tasks=%lu\n",
                phase, tasks, exit_reason, cnt, tout, tsrc, recs, out_nz, src_nz, out_ptr_ok, empty_tasks);
}
'''

if __name__ == "__main__":
    p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
    t = p.read_text()
    if MARK in t:
        print("s4207 already present")
    else:
        assert t.count(OLD) == 1
        sig = "static void rs64_s4205_rec("
        assert t.count(sig) == 1
        t = t.replace(OLD, PUSH + OLD, 1)
        t = t.replace(sig, "extern uint32_t rs64_s4207_ring[8192]; extern uint32_t rs64_s4207_n;\n" + sig, 1)
        # helper after the s4205 helper: put before musyxMixActiveVoices signature
        msig = "RECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
        assert t.count(msig) == 1
        t = t.replace(msig, HELPER + msig, 1)
        p.write_text(t)
        print("s4207 patched")
