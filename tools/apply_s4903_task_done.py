"""s4903: gfx-task begin ('B', at sp-complete) and done ('D', at dp_complete) timestamps on the
[s4899-sw] rows: b/d = ms before the swap of the first B / last D since the previous origin change,
nB/nD counts. ORIGIN: read-only counters; edits src/main/upstream_compat.cpp. Idempotent.
(The matching rs64_s4899_ev calls in lib/.../events.cpp are exported via submodule-patches.)"""
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "src/main/upstream_compat.cpp"
t = p.read_text()
if "s4903" in t:
    print("already"); raise SystemExit
def rep(a, b):
    global t
    assert t.count(a) == 1, a[:50]
    t = t.replace(a, b, 1)
rep("double tR1 = -1, tR2 = -1, tlast = 0; };", "double tR1 = -1, tR2 = -1, tlast = 0, tB = -1, tD = -1; unsigned nB = 0, nD = 0; }; // s4903")
rep("else if (kind == 'S') s.swS++;\n",
    "else if (kind == 'S') s.swS++;\n"
    "    else if (kind == 'B') { s.nB++; if (s.tB < 0) s.tB = s4902_ms(); } else if (kind == 'D') { s.nD++; s.tD = s4902_ms(); } // s4903\n")
rep('r1=%.2f r2=%.2f\\n", s.swn,', 'r1=%.2f r2=%.2f nB=%u nD=%u b=%.2f d=%.2f\\n", s.swn,')
rep("s.tR2 < 0 ? -1.0 : now - s.tR2); // s4902",
    "s.tR2 < 0 ? -1.0 : now - s.tR2,\n                     s.nB, s.nD, s.tB < 0 ? -1.0 : now - s.tB, s.tD < 0 ? -1.0 : now - s.tD); // s4902 s4903")
rep("s.tlast = now; s.tR1 = s.tR2 = -1;", "s.tlast = now; s.tR1 = s.tR2 = s.tB = s.tD = -1; s.nB = s.nD = 0;")
p.write_text(t); print("patched")
