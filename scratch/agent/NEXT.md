# NEXT work unit (s1974) — mission-entry key-sequence exploration

HYPOTHESIS-ID: mission-entry-recipe

## What s1973 settled

slotDispatcherIter was called 7659 times in 90s of hangar running with
ROGUESQ_LOG_SLOT_SP_GUARD=1; zero INVALID sp events fired. H-uninit-stack and
H-stack-collision are REFUTED in the hangar context. The SIGBUS is dormant in the
current build/recipe (two-source: s1973 sp-guard probe + s1972_hangar_300s 300s
clean soak). The M3 dispatcher SIGBUS class is now DORMANT — no active crash
families remain in the hangar recipe.

Hangar is stable 300s+ (s1972_hangar_300s: rc=0, 80 frames, no crashes).

## Single next work unit

The hangar recipe reaches the "SELECT LEVEL / AMBUSH AT MOS EISLEY" screen. It
is not known whether extending the key sequence past 11 Starts advances into the
actual mission (flight gameplay) or whether additional non-Start inputs (e.g., C
buttons, Z, L/R) are needed to confirm a mission selection. This is the first
time mission-entry is attempted.

**Goal:** Determine whether a mission can be entered from the current hangar state,
and if so, what key sequence achieves it. Mission entry would exercise:
- slotDispatcherIter with live mission NPCs (enables H-corruption-from-caller test)
- In-mission visual rendering (hologram artifact context changes)
- Any crash families unique to mission code

## Competing hypotheses and discriminator

- H-start-enters-mission: pressing Start from the mission-select screen (hangar)
  confirms the selection and enters the mission.
- H-needs-confirm-key: a non-Start button (e.g., A/C-right) is required to confirm
  before Start starts the mission.
- H-no-mission-path: the current recipe/state cannot enter a mission without
  additional setup not yet understood.

Discriminator: does the VI width change or origin change to a new scene after
additional Start presses? If a new origin (not 0x006AB400/hangar) appears after
the extra presses, mission entry occurred.

## Exact commands

Run a probe with extended Start presses after the hangar is reached:
- Current recipe reaches hangar at ~26.6s (vi_width=512 origin=0x006AB400)
- Add Start presses at 30s, 35s, 40s, 45s, 50s, 55s (6 extra beyond the eleven)
- Watch for any new [phase] VI width/origin change after 30s

```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start 62:start 67:start 72:start 77:start 82:start 87:start' \
zsh tools/probe.sh scratch/agent/s1974_mission_entry 120 2
```

Check for a new VI origin after 30s:
```sh
grep '\[phase\].*origin' scratch/agent/s1974_mission_entry/run.log | grep -v '006AB400\|00790400\|00696100\|000000'
```

If no new origin: also try C-right and A button presses (check controller button names
in tools/probe.sh or AGENTS.md). If mission-entry is achieved, record the key sequence
and the first new VI origin.

## If mission entry is not achieved

Write a 600s hangar stability soak script to scratch/agent/soak_queue/:
```sh
cat > scratch/agent/soak_queue/s1974_hangar_600s.sh << 'SOAK_EOF'
#!/bin/zsh
set -e
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/soak_results/s1974_hangar_600s_$(date +%Y%m%d-%H%M%S) 600 2
rc=$?
echo "s1974_hangar_600s: rc=$rc frames=$(ls scratch/agent/soak_results/s1974_hangar_600s_*/f_*.png 2>/dev/null | wc -l) crashes=$(grep -c SIGBUS scratch/agent/soak_results/s1974_hangar_600s_*/run.log 2>/dev/null || echo 0)"
exit $rc
SOAK_EOF
chmod +x scratch/agent/soak_queue/s1974_hangar_600s.sh
```

If mission entry is not achieved in the probe run, declare SUBSTITUTED and write
the 600s soak instead. Do not chase non-discriminating key sequences more than
once per session (iron rule 8 analog: if the probe shows no new origin after 17
Starts, one additional attempt with non-Start buttons is permitted, then stop).
