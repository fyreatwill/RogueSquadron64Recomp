#!/usr/bin/env python3
"""s6820 G3 FPS60: out-of-range NPC despawn grace is a TICK count. Every NPC update handler (24 sites) calls the range
test 0x80047D40 (0x80047DAC in parseDatItemSubtypes1To5); while it fails, a per-NPC counter (byte/half/word) is
incremented each tick and the NPC is torn down once it reaches 21 (slti/sltiu 0x15); any pass resets it. The grid-cell
scanner (updateActiveGridCellState) re-creates a torn-down NPC whose cell is still active on the next scan, so NPCs at
the edge of range churn create -> 21 ticks -> despawn -> create. 21 ticks = 0.70 s at 30 Hz but 0.35 s at ROGUESQ_FPS60:
lvl14 seed 1 (s6820) TIE creates 171 / 61 s at 30 Hz vs 445 / 63 s at FPS60, per-object re-create every 40 VI vs 20 VI,
and every create re-runs npcInitFromTemplate/initActorMotionParams (the s6815 "20-tick AI cadence" rand sites).
Fix: under ROGUESQ_FPS60 the 0x15 threshold becomes round(21 * (1/30) / dt), clamped to [21, 42], with dt = the tick's
time step captured where runInMissionFrame advances game time 0x80130BA4 (0x800FA90C, $f20). Counters stay below 127, so
the signed-byte sites (sll 24 / sra 24) are safe. ROGUESQ_FPS60_DESPAWN=0 restores; retail (no FPS60) unchanged.
Idempotent. Usage: fixup_fps60_despawn.py <RecompiledFuncs dir>"""
import pathlib, re, sys

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6820 fps60 despawn */"
DECL = "extern float rs64_tick_dt; extern int rs64_despawn_ticks(void); " + TAG + "\n"
DEF = ("extern char* getenv(const char*); float rs64_tick_dt = 1.0f / 30.0f; int rs64_despawn_ticks(void) { "
       "static int on = -1; if (on < 0) { const char* f = getenv(\"ROGUESQ_FPS60\"); const char* d = getenv(\"ROGUESQ_FPS60_DESPAWN\"); "
       "on = f && *f && *f != '0' && !(d && *d == '0'); } if (!on) return 0x15; float dt = rs64_tick_dt; "
       "if (!(dt > 0.0f) || dt >= (1.0f / 30.0f)) return 0x15; int n = (int)(21.0f / (30.0f * dt) + 0.5f); "
       "return n < 0x15 ? 0x15 : (n > 42 ? 42 : n); } " + TAG + "\n")
DT_SITE = "    // 0x800FA90C: swc1        $f2, 0xBA4($a0)\n"
DT_HOOK = "    rs64_tick_dt = ctx->f20.fl; " + TAG + "\n"
COMMENT = re.compile(r"    // 0x([0-9A-F]{8}): (\S+)\s+(.*)$")
RANGE = {"0x80047D40", "0x80047DAC"}

sites, dt_done = [], 0
for p in sorted(base.glob("funcs_*.c")):
    lines = p.read_text().splitlines(True)
    changed = False
    since = None  # instructions seen since the last range-test jal (None = not armed)
    last = None
    for i, l in enumerate(lines):
        if l.startswith("RECOMP_FUNC"):
            since = None
        m = COMMENT.match(l)
        if not m:
            continue
        key = (m.group(1), m.group(2))
        if key == last:  # delay-slot comments are emitted twice
            continue
        last = key
        if m.group(2) == "jal":
            since = 0 if m.group(3).strip() in RANGE else None
            continue
        if since is None:
            continue
        since += 1
        if since > 20:
            since = None
            continue
        if m.group(2) in ("slti", "sltiu") and m.group(3).strip().endswith(", 0x15"):
            c = lines[i + 1]
            if TAG not in c:
                if c.count("0X15") != 1:
                    sys.exit(f"s6820 fps60 despawn: unexpected compare line at {p.name}:{i + 2}: {c.strip()}")
                lines[i + 1] = c.replace("0X15", "rs64_despawn_ticks()").rstrip("\n") + " " + TAG + "\n"
                changed = True
            sites.append(m.group(1))
            since = None
    s = "".join(lines)
    if DT_SITE in s:
        if s.count(DT_SITE) != 1:
            sys.exit(f"s6820 fps60 despawn: dt site count {s.count(DT_SITE)} in {p.name}")
        if DT_HOOK not in s:
            s = s.replace(DT_SITE, DT_HOOK + DT_SITE, 1)
            changed = True
        if DEF not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DEF, 1)
            changed = True
        dt_done += 1
    elif changed and DECL not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
    if changed:
        p.write_text(s)
if dt_done != 1:
    sys.exit(f"s6820 fps60 despawn: dt site found in {dt_done} files (want 1)")
if len(sites) != 24:
    sys.exit(f"s6820 fps60 despawn: expected 24 despawn compares, found {len(sites)}: {sites}")
print(f"[s6820] fps60 despawn grace: {len(sites)} compares scaled by tick dt")
