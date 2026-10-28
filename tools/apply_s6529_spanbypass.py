"""s6529: land the s6527/s6528 span-reject bypass as a ROGUESQ_DRAW_DISTANCE>1 default.
streamTerrainGridCellsByDistance's compares at 0x80042D8C/0x80042DA4 reject visible terrain cells at dd>1 (s6528: tight fraction 0.047 -> 0.209 when forced).
Default: bypass iff ROGUESQ_DRAW_DISTANCE>1; ROGUESQ_SPAN_BYPASS=0 opts out; ROGUESQ_SPANFORCE (1|toggle) still overrides. dd<=1 stays bit-identical retail.
Self-contained: applies the s6527 helper+sites if absent, then swaps in the new default."""
from pathlib import Path
import subprocess, sys
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
if "s6529 spanbypass" in T:
    print("already"); raise SystemExit(0)
if "s6527 spanforce" not in T:
    sys.path.insert(0, str(Path(__file__).parent))
    import apply_s6527_spanforce  # noqa: F401  (applies on import, module-level script)
    T = P.read_text()
old = "e = (s && *s) ? ((s[0]=='t') ? 2 : 1) : 0;"
new = ("e = (s && *s) ? ((s[0]=='t') ? 2 : 1) : 0; /* PATCH: s6529 spanbypass */ "
       "if (!e) { const char* b = getenv(\"ROGUESQ_SPAN_BYPASS\"); const char* d = getenv(\"ROGUESQ_DRAW_DISTANCE\"); if (!(b && b[0]=='0') && d && atof(d) > 1.0) e = 1; }")
assert T.count(old) == 1
P.write_text(T.replace(old, new, 1)); print("ok")
