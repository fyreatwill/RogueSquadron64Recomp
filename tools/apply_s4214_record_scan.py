"""s4214: scan all 96 0x50-byte records at data_ptr+0x30 per audio task: ASCII/zero fractions, changed-bytes vs previous task, first non-ASCII record. Env ROGUESQ_LOG_S4213=1 (shares gate)."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
t = rsp.read_text()
if "rs64_s4214_scan" not in t:
    anchor = "static void rs64_s4213_census(const OSTask* task) {\n"
    assert t.count(anchor) == 1
    fn = r'''static void rs64_s4214_scan(uint8_t* rdram, const OSTask* task, uint32_t phase, unsigned n) {
    static uint8_t prev[96 * 0x50 + 0x30]; static uint32_t prev_dp; static bool have;
    uint32_t dp = (uint32_t)task->t.data_ptr; uint32_t off = dp & 0x1FFFFFFFu;
    if (off == 0 || off + sizeof(prev) > 0x800000u) return;
    const uint8_t* b = rdram + off;
    uint8_t cur[sizeof(prev)];
    for (size_t i = 0; i < sizeof(cur); i++) cur[i] = b[i ^ 3]; // guest byte order (rdram word-swapped)
    unsigned ascii = 0, zero = 0, ascii_recs = 0, zero_recs = 0, changed = 0, first_non = 96, first_nz_non = 96;
    for (unsigned r = 0; r < 96; r++) {
        unsigned a = 0, z = 0;
        for (unsigned k = 0; k < 0x50; k++) { uint8_t c = cur[0x30 + r * 0x50 + k]; if (c >= 0x20 && c < 0x7F) a++; if (c == 0) z++; }
        ascii += a; zero += z;
        if (z == 0x50) zero_recs++;
        if (a >= 0x30) ascii_recs++; else { if (first_non == 96) first_non = r; if (z != 0x50 && first_nz_non == 96) first_nz_non = r; }
    }
    if (have && prev_dp == dp) for (size_t i = 0; i < sizeof(cur); i++) changed += cur[i] != prev[i];
    else changed = 0xFFFFFFFFu;
    memcpy(prev, cur, sizeof(cur)); prev_dp = dp; have = true;
    if (n <= 6 || (n & (n - 1)) == 0) {
        std::fprintf(stderr, "[s4214-scan] phase=%u n=%u dp=0x%08X ascii_bytes=%u zero_bytes=%u ascii_recs=%u zero_recs=%u first_nonascii_rec=%u first_nz_nonascii_rec=%u changed=%d hdr=%02X%02X%02X%02X rec0=%02X%02X%02X%02X%02X%02X%02X%02X\n",
            phase, n, dp, ascii, zero, ascii_recs, zero_recs, first_non, first_nz_non, (int)changed,
            cur[0], cur[1], cur[2], cur[3], cur[0x30], cur[0x31], cur[0x32], cur[0x33], cur[0x34], cur[0x35], cur[0x36], cur[0x37]);
    }
}
'''
    t = t.replace(anchor, fn + anchor)
    call = ("rs64_s4213_census(task);\n"
            "    { static const bool on2 = [] { const char* e = std::getenv(\"ROGUESQ_LOG_S4213\"); return e && e[0] && e[0] != '0'; }();"
            " static uint32_t pk = 0xFFFFFFFFu; static unsigned sn;"
            " if (on2) { uint32_t ph = rs64_phase_ord(); if (ph != pk) { pk = ph; sn = 0; } rs64_s4214_scan(rdram, task, ph, ++sn); } }\n")
    assert t.count("    rs64_s4213_census(task);\n") == 1
    t = t.replace("rs64_s4213_census(task);\n", call, 1)
    rsp.write_text(t); print("patched")
