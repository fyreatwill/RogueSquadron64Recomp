#!/usr/bin/env python3
"""s5379: positive control for the s5370 path census.

ORIGIN: s5370/s5378 read slot0=g2=g3=0 on every row, i.e. the head/walk guard sites were never
reached, but no same-run control proved the slot0/g2/g2bad/g3/g3bad counters can fire at all.
With ROGUESQ_A5370_CTL=1, every 64th function entry has its cached-slot register forced to 0
(the empty-slot path), so slot0 and (if the unlink returns non-null) g2/g3 must go nonzero.
Control-only (env-gated, default off). Idempotent. Run after apply_s5370_path_census.py on the
RecompiledFuncs dir."""
import re, sys, pathlib

MARK = "PATCH: s5379 census ctl"
pat = re.compile(r'(    a5370_ent\+\+; if \(ctx->r(\d+) == 0\) a5370_slot0\+\+;)')


def rep(m):
    r = m.group(2)
    return (f'    {{ static int a5379_ctl = -1; if (a5379_ctl < 0) {{ const char* e = getenv("ROGUESQ_A5370_CTL"); '
            f'a5379_ctl = (e && e[0] && e[0] != \'0\') ? 1 : 0; }} '
            f'if (a5379_ctl && ((a5370_ent + 1u) & 63u) == 0) ctx->r{r} = 0; }} /* {MARK} */\n' + m.group(1))


tot = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob("funcs_*.c")):
    t = p.read_text()
    if MARK in t or 'PATCH: s5370 path census' not in t:
        continue
    t, n = pat.subn(rep, t)
    if n:
        p.write_text(t)
        tot += n
        print(p.name, n)
print("patched", tot)
