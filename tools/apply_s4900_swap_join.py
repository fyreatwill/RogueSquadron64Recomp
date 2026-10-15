"""s4900: per-origin-change (osViSwapBuffer fb change) R/S histogram rows [s4899-sw].
ORIGIN: read-only counters; edits src/main/upstream_compat.cpp (not generated code). Idempotent."""
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "src/main/upstream_compat.cpp"
t = p.read_text()
if "rs64_s4899_swap" in t:
    print("already"); raise SystemExit
def rep(a, b):
    global t
    assert t.count(a) == 1, a[:50]
    t = t.replace(a, b, 1)
rep('    if (n <= 16 || (n & 63) == 0) {\n        fprintf(stderr, "[osViSwapBuffer #%d] fb=0x%08X\\n", n, fb);',
    '    rs64_s4899_swap(fb, rs64_vi_committed_width()); // s4900\n    if (n <= 16 || (n & 63) == 0) {\n        fprintf(stderr, "[osViSwapBuffer #%d] fb=0x%08X\\n", n, fb);')
rep('extern "C" void osViSwapBuffer_recomp(uint8_t* rdram, recomp_context* ctx) {\n    static int s_count',
    'extern "C" void rs64_s4899_swap(uint32_t fb, uint32_t width);\nextern "C" void osViSwapBuffer_recomp(uint8_t* rdram, recomp_context* ctx) {\n    static int s_count')
rep('struct S4899 { std::mutex m; unsigned cnt[128] = {}; std::string order; };',
    'struct S4899 { std::mutex m; unsigned cnt[128] = {}; std::string order; unsigned swR = 0, swS = 0, swn = 0; uint32_t lastfb = ~0u; };')
rep("    s.cnt[(unsigned char)kind & 127]++;\n",
    "    s.cnt[(unsigned char)kind & 127]++;\n    if (kind == 'R') s.swR++; else if (kind == 'S') s.swS++;\n")
rep('extern "C" void rs64_s4899_vi(',
    '''// s4900: one row per osViSwapBuffer that CHANGES the framebuffer (true origin change).
extern "C" void rs64_s4899_swap(uint32_t fb, uint32_t width) {
    if (!s4899_on()) return;
    auto& s = s4899(); std::lock_guard<std::mutex> g(s.m);
    s.swn++;
    if (fb != s.lastfb) {
        std::fprintf(stderr, "[s4899-sw] n=%u width=%u fb=0x%08X R=%u S=%u\\n", s.swn, width, fb, s.swR, s.swS);
        s.swR = 0; s.swS = 0; s.lastfb = fb;
    }
}
extern "C" void rs64_s4899_vi(''')
p.write_text(t); print("patched")
