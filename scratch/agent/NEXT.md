# NEXT: guest-PC writer census for the non-health fail setters

One bounded work unit: replace the invalid host-symbol LLDB witness with one
regeneration-presistent entry census at guest PCs 0x800B0348,
0x800B08DC, and 0x800FB2B0. First inspect the current generated bodies and
the retail/static call sites; do not build until the guest-PC locations and
argument registers are independently confirmed. Add the diagnostics to the
appropriate fixup script, regenerate in the documented order, build once, and
run the same 420 s mission recipe with the positive controls `[mtm]` and lives
decrement required.

Competing hypotheses and the discriminating measurement:

- H1: the player craft reaches 0x800B0348 and sets slot bit 0x10. Evidence:
  an entry line for guest PC 0x800B0348 with a0==0x80137DBC before a lives
  decrement.
- H2: only the NPC destruction setter at 0x800B08DC reaches the path. Evidence:
  entry lines at 0x800B08DC with a0 != 0x80137DBC before the same control.
- H3: neither setter executes; the transition is caused by the bit-1 settle
  chain or another writer. Evidence: `[mtm]`/lives control fires while both
  setter-PC counters are zero, with the bit-1 writer census identifying the
  preceding guest PC.

The split is one run: every setter entry must print guest PC, a0, slot-state
halfword, and a monotonic ordinal; mtm/lives lines are the positive controls.
Do not infer H3 from absent host-symbol breakpoints. Capture output under
`scratch/agent/m6/<tag>/`, kill with SIGKILL, and require the mission origin
before counting any setter hit.

Expected commands after the static/ground-truth check:

```zsh
rg -n '800B0348|800B08DC|800FB2B0' RecompiledFuncs tools/fixup_game_funcs_vendored.py
python tools/<new guest-pc-census-fixup>.py
cmake --build build --config Debug --target RogueSquadron64Recomp
env XENV='ROGUESQ_LOG_MTM=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_GODMODE=1 ROGUESQ_GODMODE3=2' zsh scratch/agent/<guest-pc-soak>.sh
```

HYPOTHESIS-ID: g1-nonhealth-fail
