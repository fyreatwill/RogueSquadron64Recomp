# NEXT: qualify the s5818 NPC-health diagnostic guard class

HYPOTHESIS-ID: m3-s5818-health-read-guard

Work unit: add a regeneration-safe guest-pointer guard before the existing
s5818 `npcGroundTroopUpdate` health probe, update the live generated function,
and build `RogueSquadron64Recomp`. Do not run a new soak: this is a bounded
guard-class audit, not a diagnostic rerun.

Competing hypotheses:

- H1: `ctx->r17` or `[s1+0x38]` can be stale/non-KSEG0 at the diagnostic call,
  so the probe can fault before the game health path is tested.
- H2: only the nested health-array calculation is unsafe; the object and slot
  pointers are always valid at this call site.
- H3: all three pointers are valid and the prior fault cannot recur in this
  call site; a guard would be unjustified.

Discriminator: static dataflow plus the existing crash evidence. H1 selects if
the call can reach `getNpcCurrentHealth` with an invalid object/slot or nested
health address; H2 selects if only the nested address can be invalid; H3 would
reject the guard. The positive control is the existing s5818 fault evidence
and the unchanged `s5818` in-range probe path; no new counter is needed.

Evidence consumed before building: the `s5845/s5870/s5872` records identify
stale NPC slots as the diagnostic fault source, and the current `rs5818_gt`
body dereferences `s1`, `[s1+0x34]`, and `[s1+0x38]` before the health call.
The game-side writer is `npcGroundTroopUpdate`/teardown; the new guard only
protects our read and does not filter or mutate game state.

Exact preflight/build commands:

```sh
rg -n 'rs5818_gt|t\.r4 = MEM_W\(s1, 0X38\)' tools/apply_s5818_destroy_health.py ../N64Recomp/RecompiledFuncs/funcs_39.c
python3 -m py_compile tools/apply_s5818_destroy_health.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Expected outcomes: the source patch and generated function both contain the
same pointer/range checks, and the normal build succeeds. A future s5818 run
must show the valid in-range path still logging while stale slots are skipped;
this iteration does not claim a mission-coverage result.
