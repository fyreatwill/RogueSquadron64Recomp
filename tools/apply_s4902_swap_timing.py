"""s4902: wall-clock ms on [s4899-sw] rows: swap time, dt since previous origin change, and
times of the first two R (retrace-return) events in the interval relative to the swap.
ORIGIN: read-only counters; edits src/main/upstream_compat.cpp. Idempotent."""
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "src/main/upstream_compat.cpp"
t = p.read_text()
if "s4902" in t:
    print("already"); raise SystemExit
def rep(a, b):
    global t
    assert t.count(a) == 1, a[:50]
    t = t.replace(a, b, 1)
rep("unsigned swR = 0, swS = 0, swn = 0; uint32_t lastfb = ~0u; };",
    "unsigned swR = 0, swS = 0, swn = 0; uint32_t lastfb = ~0u; double tR1 = -1, tR2 = -1, tlast = 0; };\n"
    "static double s4902_ms() { using C = std::chrono::steady_clock; return std::chrono::duration<double, std::milli>(C::now().time_since_epoch()).count(); } // s4902")
rep("    if (kind == 'R') s.swR++; else if (kind == 'S') s.swS++;\n",
    "    if (kind == 'R') { s.swR++; double n = s4902_ms(); if (s.tR1 < 0) s.tR1 = n; else if (s.tR2 < 0) s.tR2 = n; } else if (kind == 'S') s.swS++;\n")
rep('''        std::fprintf(stderr, "[s4899-sw] n=%u width=%u fb=0x%08X R=%u S=%u\\n", s.swn, width, fb, s.swR, s.swS);
        s.swR = 0; s.swS = 0; s.lastfb = fb;''',
    '''        double now = s4902_ms();
        std::fprintf(stderr, "[s4899-sw] n=%u width=%u fb=0x%08X R=%u S=%u dt=%.2f r1=%.2f r2=%.2f\\n", s.swn, width, fb, s.swR, s.swS,
                     now - s.tlast, s.tR1 < 0 ? -1.0 : now - s.tR1, s.tR2 < 0 ? -1.0 : now - s.tR2); // s4902
        s.tlast = now; s.tR1 = s.tR2 = -1;
        s.swR = 0; s.swS = 0; s.lastfb = fb;''')
if "#include <chrono>" not in t:
    t = "#include <chrono>\n" + t
p.write_text(t); print("patched")
