# NEXT: audit the next complete unguarded indexed-dereference idiom
HYPOTHESIS-ID: m3-idiom-class-audit

The s4674 self-referential-walk class is closed provisionally: 30 sites in 14
functions, no invalid writer established, no guard added. Do not repeat it.

Before any build, enumerate one complete remaining indexed-dereference class
from `../N64Recomp/RecompiledFuncs/` and write its competing hypotheses here.
Use a fresh scan (not `find_unguarded_walks.py`) and a same-source positive
control from an already guarded indexed site. Classify every site by index
source, bound/sentinel, writer, and legitimacy. If no complete class and
positive control can be named, write BLOCKED instead of adding instrumentation.

Exact starting commands:

    rg -n 'MEM_[BHW]\\(ctx->r[0-9]+, 0X[0-9A-F-]+\\)' ../N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n -i 'guard|KSEG|sltiu|sltu|andi.*0xFF' ../N64Recomp/RecompiledFuncs/funcs_*.c

Expected discriminator: zero sites with a reachable noncanonical index selects
the safe-loop arm; one or more sites with a named writer that can publish an
out-of-range index selects a concrete guard/patch candidate; a census mismatch
or missing positive control blocks the unit.
