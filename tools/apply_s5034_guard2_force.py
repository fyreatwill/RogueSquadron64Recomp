#!/usr/bin/env python3
"""s5034: add ROGUESQ_FORCE_ALLOC_TAIL_GUARD2 (log-only positive control) to the live guard2 blocks.
Idempotent. Usage: apply_s5034_guard2_force.py <RecompiledFuncs dir>. Same change lives in
fixup_game_funcs_vendored.py for regens. Force makes the guard LOG every pass but never take the goto."""
import re, sys, pathlib
pat = re.compile(
    r'(        uint32_t (r\d+)_lo = U32\(ctx->\2\);\n)'
    r'        if \(\2_lo < 0x80000000u \|\| \2_lo >= 0x80800000u\) \{\n'
    r'(            if \(s_alloc_tail_guard2_enabled\) \{\n.*?\n            \}\n)'
    r'            goto (\w+);\n        \}\n', re.S)
def rep(m):
    h = m.group(2)
    return (m.group(1) +
            '        static int s_alloc_tail_guard2_force = -1;\n'
            '        if (s_alloc_tail_guard2_force < 0) { const char* e = getenv("ROGUESQ_FORCE_ALLOC_TAIL_GUARD2"); s_alloc_tail_guard2_force = (e && e[0] && e[0] != \'0\') ? 1 : 0; }\n'
            f'        if ({h}_lo < 0x80000000u || {h}_lo >= 0x80800000u || s_alloc_tail_guard2_force) {{\n' +
            m.group(3) +
            f'            if ({h}_lo < 0x80000000u || {h}_lo >= 0x80800000u) goto {m.group(4)};  // force = log only\n        }}\n')
tot = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob("funcs_*.c")):
    t = p.read_text()
    if 'alloc-tail-guard2' not in t:
        continue
    t2, n = pat.subn(rep, t)
    if n:
        p.write_text(t2); tot += n; print(p.name, n)
print("patched", tot)
