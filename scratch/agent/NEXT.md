# NEXT: level-1 named forced-victim objective response
HYPOTHESIS-ID: g1-coverage-cd

One bounded adapter generalization plus ONE forced-level-1 flight. Reuse
s6657's complete off/on/off and actual-store join; do not build a new
instrument one field at a time. Level0 now has eight complete triads and
13 live readbacks (docs/G1-OBJECTIVE-RESPONSE.md), single-source dynamic
response. Do not repeat it or tune aim, steering, wins or progression.

Competing hypotheses:
- H-response: an actual objective counter read by the lv1 callback changes
  for a forced victim, with descriptor index/delta semantics supporting it.
- H-incidental: the changes are baseline, Boolean-only, failure-related or
  counters not used by lv1's objectives (saved id13 meaning is unresolved).
- H-route/control: forced selector/callback or live changing-value control
  is absent. This outcome is unevaluated, never a controlled null.

Discriminator: ONE event table joins explicit selected flight epoch + VI +
off/on/off arm + forced shape/projectile + parent node + NPC payload +
descriptor + accepted hit SEND + actual writer PC/index/old/new + callback
readback. Exact victim/index/delta identity, not arm rates, selects response.
Classify success/failure semantics from the original ELF before running.

Ground truth and boring checks first:
    wc -c < docs/CURRENT-TRUTH.md
    sed -n '1,100p' docs/G1-OBJECTIVE-RESPONSE.md
    sed -n '1,100p' docs/M6-OBJECTIVE-COUNTER-WRITERS.md
    sed -n '1,200p' tools/apply_s6657_objective_response.py
    sed -n '1,160p' tools/g1_objective_response_run.py
    rg -n 'RECOMP_FUNC void lv1_(checkComplexObjectives|calculateFriendliesSaved|objectiveSlot1)' ../N64Recomp/RecompiledFuncs/funcs_43.c
Read bounded windows around those hits (never whole generated files),
extract their guest PCs, and inspect the ORIGINAL ELF, <=60 lines/output:
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf <start> <stop>
Read docs/debug-trace-env-vars.md before adding logging. Existing oracle
is undriven in missions; a boot-only null is not a witness.

Implement explicit ROGUESQ_OBJECTIVE_RESPONSE_LEVEL=1 (default 0 preserves
s6657) in the existing adapter, a lv1 callback hook, and --level 1 in the
existing runner (both currently hardcode level0). Scope the full selected
counter readback to the flight; seven actual stores already cover the known
writer class. Do not assume counters 1..3 suffice for lv1. Pick conservative
stop limits from the original callback gates; stop well below success or
failure/end gates. If necessary stop after the first full named response.
The existing 0/1800/4200/5400 VI windows are flight-relative, not wall-clock.
Resolve slots as table[id*8] -> parent; parent+4 -> NPC; NPC+0x34 -> desc.
Attribution may use exact s-register identity plus live descriptor equality;
label it as a join, not an independently observed call stack. Keep the
accepted [eff2] SEND witness; it must visibly fire in the measured arm.
The legacy health helper can read meaningless values on some objects; it
is NOT damage proof. The lever includes NPC bolts (w hardcoded0), so do not
claim player shots or aim. Nulls still require live value-detection controls.

Persist every generated hook through the fixup replay, apply to the live
tree and build once (fix any actual implementation failure this iteration):
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
If regenerating, obey make_elf -> N64Recomp -> fixup -> cmake; do not run
full fixup on the existing tree. Preserve submodule patches.

AFTER the above CLI/adapter generalization exists, exact planned run:
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    python3 tools/g1_objective_response_run.py s6658_response --level 1
    python3 tools/g1_objective_response_run.py s6658_response --level 1 --analyze
The wrapper must update its output path to g1_lvl1s6658_response; refuse
reuse, record binary/source/env manifest, run from build/ with ROM, watchdog
itself and SIGKILL the recipe group at done (360s hard timeout). Screen must
be unlocked. All arms belong to this one flight. No repeat-soak queue needed.

Expected outcomes: a complete force/SEND/store/readback chain for a named
lv1 objective counter selects H-response; classified failure/other activity
selects H-incidental. Missing identity/control stays unknown. Record every
failed arm or hook honestly. No full VERIFIED promotion on single-source
retail equivalence, no mission completion, no default-setting change.
