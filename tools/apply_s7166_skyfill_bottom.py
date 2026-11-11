#!/usr/bin/env python3
"""s7166 G3 21:9 L4 cutscene lower-right hole: the s7136 sky fill rect must keep the builder's own bottom/right edges.

ORIGIN (s7166, three same-recipe L4 runs with the letterbox ring trigger ROGUESQ_G5B_FRAME_TRIG_LB): in the letterboxed
mid-mission cutscene (X-wing low over water) the horizon clear builder 0x8005B51C emits its x-split pair, e.g. 4:3
{256,230,511,393} {0,230,255,393}: both reach row 393, the bottom of the 340-row viewport that starts at y 54 (the viewport
struct at 0x80138D20 holds w 1024 at +0x12 and h 340 at +0x16). s7136 SKYFILL overwrites the pair's first rect with
{0, 0, w-1, h-1} = {0,0,1023,339}: h-1 is a HEIGHT, used as an absolute bottom row. The right below-horizon rect is gone, so rows 340-392 right of the
split stay uncleared, and in the ~1 s where no water/terrain tri reaches the bottom 53 rows (0 tris there at 21:9 AND 4:3, s7166) the
replay leaves 512 x 53 = 27136 px unpainted and RT64 shows a stale smear. 4:3 retail (no SKYFILL) peaks at 338 px; CULL_SPIKE=0 is byte-identical (not the cull).
In flight the viewport starts at y 0, so h-1 is the true bottom and s7136's result there is unchanged.
Fix: the widened rect's y1 / x1 are max(h-1, y1 of either builder rect) / max(w-1, x1 of either), read before the overwrite.
  ROGUESQ_HORIZON_SKYFILL_BOT: default on (acts only where SKYFILL acts, i.e. ASPECT k != 1); =0 restores s7136; =tog odd mach seconds.
Idempotent; listed in fixup_game_funcs_vendored.py right after apply_s7136_sky_fill.py."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7166 skyfill bottom"
P = BASE / "funcs_13.c"
T = P.read_text()
if MARK in T:
    print("s7166 already applied"); sys.exit(0)
assert "PATCH: s7136 sky fill" in T, "s7136 must be applied first"
OLD = "              MEM_H(0, r) = 0; MEM_H(2, r) = 0; MEM_H(4, r) = (int16_t)(w - 1); MEM_H(6, r) = (int16_t)(h - 1); n7136++; } } } } }\n"
assert T.count(OLD) == 1, "s7136 store line not found"
NEW = ("              { /* " + MARK + " */ static int md7166 = -1; if (md7166 < 0) { const char* e = getenv(\"ROGUESQ_HORIZON_SKYFILL_BOT\"); md7166 = (e && *e == '0') ? 0 : (e && !strcmp(e, \"tog\")) ? 2 : 1; }\n"
       "                int x1 = w - 1, y1 = h - 1;\n"
       "                if (md7166 == 1 || (md7166 == 2 && ((mach_absolute_time() / 24000000ull) & 1))) {\n"
       "                  int a = (int16_t)MEM_H(4, r), b = (int16_t)MEM_H(12, r), c2 = (int16_t)MEM_H(6, r), d = (int16_t)MEM_H(14, r);\n"
       "                  if (a > x1 && a < 2048) x1 = a; if (b > x1 && b < 2048) x1 = b; if (c2 > y1 && c2 < 1024) y1 = c2; if (d > y1 && d < 1024) y1 = d; }\n"
       "                MEM_H(0, r) = 0; MEM_H(2, r) = 0; MEM_H(4, r) = (int16_t)x1; MEM_H(6, r) = (int16_t)y1; n7136++; } } } } } }\n")
T = T.replace(OLD, NEW, 1)
P.write_text(T); print("s7166 applied")
