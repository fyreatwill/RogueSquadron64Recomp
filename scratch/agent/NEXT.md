# NEXT work unit

HYPOTHESIS-ID: m3-dod-craft-stick-hold

## s575 recap (read this first)

**Item -7: H-exit5 REFUTED. Leave Start advances case 3→5; case 5 waits.**

Positive control: hangarbay n=900; hangar-state 0→1→3→5; state-write AC1C4 3→5
same frame as `[buttons-hangar] AC0F0 a_start=1 n=718`.
case5-entry n=0..213 after leave; AC8C0 polls ≥200 with **0** a_start=1.
0 hangar-sel, 0 graceful-menu. Driver `start_only` sends only one Start.
H-exit5/5a/5b REFUTED. H-exit6 NEW (need 2nd Start). H-exit1 testable on 2nd Start
(ship-active early samples ret=1 / ship=0x8015FD90).

case3-start re-read values are junk — trust state-write + hangar-state only.

## This iteration's work unit

**Item -7 — double-Start leave: does case-5 confirm fire hangar-sel?**

No new build required if s575 probes still in binary (hangar-state / state-write /
case5-entry / buttons-hangar / hangar-sel / ship-active). Rebuild only if tree was
regenerated.

### Hypotheses
- H-exit6a: 2nd Start at AC8C0 with ship-active ret=0 → hangar-sel write + progress.
- H-exit6b: 2nd Start never reaches AC8C0 (timing / not in case 5 / input drop).
- H-exit1: 2nd Start reaches AC8C0 but isPlayerShipActive ret=1 → skip hangar-sel
  (bne L_800AC950 at AC8D8).
- H-exit6c: 2nd Start + ret=0 but hangar-sel still 0 (deeper gate past AC914).

### Discriminating measurements (existing probes)
| outcome | evidence |
|---------|----------|
| 6a | a_start=1 @ AC8C0 + hangar-sel fire + (optional) graceful-menu / non-sentinel frame-ret |
| 6b | case5-entry alive but AC8C0 never a_start=1 on 2nd press |
| H-exit1 | a_start=1 @ AC8C0 + ship-active ret=1 same window + 0 hangar-sel |
| 6c | a_start=1 + ship-active ret=0 + 0 hangar-sel |

Positive control: hangar-state reaches 5 after 1st Start; case5-entry increments;
2nd Start must show AC8C0 a_start=1.

### Exact commands
```bash
# Prefer explicit two-Start probe list. If script has no PROBES env override,
# temporarily set in run_mission_keys or use:
#   PROBES=(p1:start:3 p2:start:8)  inside a thin wrapper.
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# Option A — mixed ends with a 2nd Start after A (may work; A is likely noop in case 5):
env PROBE_MODE=mixed HOLD_S=15 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s576_item7_double_start 5 12

# Option B (preferred if A is ambiguous): edit PROBES for one run to
#   PROBES=(p1:start:3 p2:start:10)
# without the middle A.

grep -E 'hangar-state|state-write|case5-entry|buttons-hangar|ship-active|hangar-sel|graceful-menu|frame-ret' \
  scratch/s73_post_a_scene/s576_item7_double_start/run.log | \
  grep -E 'a_start=1|state=5|old=3 new=5|hangar-sel|graceful|sentinel=0|ship-active' | head -80
```

Also log ship-active on every call during case 5 if rate-limit hides ret at confirm
time (raise: always log when ret changes OR force first 20 after hangar-state=5).

### Expected outcomes
- 6a: hangar-sel fires → next unit = mission overlay / post-exit path (H1 follow-up).
- H-exit1: need to clear gPlayerShip / understand why ship ptr is set on menu craft.
- 6b: fix input timing (longer gap, hold Start, re-raise).
- 6c: read case-5 body past AC8D8.

### Do NOT
- Chase 0x8000afa0 / -338.
- Blind stick HOLD_S=60 before double-Start works.
- Reopen M5 / freelist residual.
- Trust case3-start MEM_BU re-read fields (state=89 junk).
