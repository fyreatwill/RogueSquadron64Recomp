"""s6698 G1c: gate the per-guest-store diagnostic hooks behind one global int (g_rs64_store_diag, main.cpp).
The fixup chain emits ~94k scalar hook calls (rs64_m5_writer_parity / rs64_probe_submit_gate_store / s65xx notes) and
~49k s6336 F5 post-store calls, i.e. 3-5 out-of-line calls on EVERY guest store, armed or not. A 10 s `sample` of lvl5
dd4 flight put 52% of the game thread's busy time in that chain (scanConvertTriangleToSpanTable alone). Each call line
is now prefixed with `if (__builtin_expect(g_rs64_store_diag, 0))` and the RS64_S5798_ST macro breaks out first.
Policy lives in main.cpp (auto-on whenever a logging/watch env var is set). Observation-only hooks; no game semantics."""
from pathlib import Path
import re, sys
D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "/* PATCH: s6698 storediag */"
GATE = "if (__builtin_expect(g_rs64_store_diag, 0)) "
P1 = re.compile(r'^(\s*)((?:rs64_m5_writer_parity|rs64_probe_submit_gate_store|s6512_note_writer|s6500_note_writer|s6499_note|s6521_note)\(.*\);\s*(?:/\*.*\*/)?\s*)$')
P2 = re.compile(r'^(\s*)(\{ extern void rs64_f5_store_shadow_post\(char, uint32_t, uint32_t\); rs64_f5_store_shadow_post\(.*\); \}.*)$')
BRACELESS = re.compile(r'^\s*(if\s*\(.*\)|else|else if\s*\(.*\))\s*$')
files = gated = macros = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if MARK in t:
        continue
    L = t.split("\n"); k = 0
    for i, l in enumerate(L):
        m = P1.match(l) or P2.match(l)
        if not m:
            continue
        if BRACELESS.match(L[i - 1]):
            sys.exit(f"s6698: braceless if/else before hook at {p.name}:{i + 1}")
        L[i] = m.group(1) + GATE + m.group(2); k += 1
    t = "\n".join(L)
    t, mk = re.subn(r"(#define RS64_S5798_ST\(pc, off, base, w\) do \{ )", r"\1if (!__builtin_expect(g_rs64_store_diag, 0)) break; ", t, count=1)
    if not k and not mk:
        continue
    t = t.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + MARK + "\nextern int g_rs64_store_diag;\n", 1)
    if MARK not in t:
        sys.exit(f"s6698: no recomp.h include in {p.name}")
    p.write_text(t); files += 1; gated += k; macros += mk
print(f"[s6698] storediag: files={files} gated={gated} macros={macros}")
# post-condition: no ungated hook call line remains
left = [f"{p.name}:{i + 1}" for p in sorted(D.glob("funcs_*.c")) for i, l in enumerate(p.read_text().split("\n"))
        if (P1.match(l) or P2.match(l))]
if left:
    sys.exit(f"s6698 post-condition: ungated hook lines {left[:3]}")
