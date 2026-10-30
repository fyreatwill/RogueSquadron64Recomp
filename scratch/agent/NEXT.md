# G1(d): qualify one named level-2 loss response
HYPOTHESIS-ID: g1-coverage-cd

Maintenance s6667 is complete: CURRENT-TRUTH 61170->34276 bytes,
708->370 lines (338 net removed). Four exact blocks moved verbatim to
PROJECT-OVERVIEW, Maintenance s6667 retained evidence. No game/build ran.
No new soak verdicts. Resume this one bounded unit, not maintenance.

Known boundary: s6666 timer1 reset/tick/getters pass; old5401VI only55.55,
gate opens at9839VI/100.033333. Rescue01 DAT+1510, D3894 handler, canonical
slot254 in that run; ordinary exact seq1 force/SEND reduces2000->1990.
Counter40 is friendly loss; its first positive value triggers failure.
Current adapter hard-disables level2 lethal dosing. Do not merely enable
it: audit original death/callback/end ordering first. No win/progression.

Competing hypotheses and one discriminating table:
- H-dose: surviving health is the only missing boundary. Exact ordinary
  hit then one currentHP+1 damage request on that same owned rescue01
  produces original death/effect, counter40 store0->1 and callback readback.
- H-routing: ordinary control passes, but death branch does not reach the
  descriptor effect or writes a different id. Exact actor/projectile/seq/
  node/NPC/descriptor plus original branch trace splits this from H-dose.
- H-observation: actual counter40 store occurs, but callback readback or
  analyzer misses it. Compare raw original store and actual getter/readback
  with same-flight changing-value controls, not just callback entry counts.
Discriminator: ordinary force->accepted SEND->health delta, then same-owned
one-shot dose->real health return->death effect->original counter40 store
->callback readback, with VI/arm and identity joins at every boundary.
Missing ordinary control or missing changing-value controls is inconclusive.
Original ELF/DAT are independent contracts; dynamic causality remains
single-flight evidence. Do not claim retail equivalence/full VERIFIED.

First inspect original message5 target800D49FC and callback80102174..226C,
following calls/branches until effect versus failure/end ordering is clear.
If callback readback cannot be observed before failure/end handling without
changing mission state, redesign the stopping boundary before a run. Do not
suppress the game's failure, write counters/Booleans/timers/health, or choose
an arbitrary victim. At most one dose, forces inhibited immediately afterward.
Default level2 remains ordinary-only. Carry all existing timer/gate/ownership/
SEND/health/store/readback/mark-all controls in the same build.

Exact starting commands (repo root; bounded reads only):
    mkdir -p scratch/agent/s6668_lvl2_loss
    python3 tools/g1_dat_inventory.py --check-level2 --level 2 --output scratch/agent/s6668_lvl2_loss/original.json
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800D49FC 0x800D4D00 > scratch/agent/s6668_lvl2_loss/shuttle.txt
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80102174 0x80102270 > scratch/agent/s6668_lvl2_loss/callback.txt
    rg -n 'rs6661_dosed|rs6661_target|rs6664_transport_common|rs6660_observed' tools/apply_s6657_objective_response.py
    sed -n '330,389p' tools/apply_s6657_objective_response.py
    sed -n '876,935p' docs/G1-OBJECTIVE-RESPONSE.md

Implement the bounded opt-in only after that audit, including analyzer
positive/negative fixtures for wrong identity, missing ordinary control,
missing actual store/readback and a second dose. Use fixup tooling for any
generated edit. Existing adapter can be reapplied via:
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
If full regeneration is necessary, keep make_elf -> N64Recomp ->
fixup_game_funcs -> cmake order; do not regenerate just for a probe edit.

Only after original ordering and stop mechanism pass, one same-flight run:
    env ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1 python3 tools/g1_objective_response_run.py s6668_loss --level 2 --flight-vi 12000
    python3 tools/g1_objective_response_run.py s6668_loss --level 2 --flight-vi 12000 --analyze
Runner checks CGSSessionScreenIsLocked, uses build/ ROM,600s watchdog and
SIGKILL; fresh tag required. Keep retail aspect/dd/FPS settings and inspect
manifest for inherited env flags before launch. Do not repeat an ordinary-only
12000VI flight unless the new instrument is ready to split hypotheses.
Record complete arm table and evidence limits, update CURRENT-TRUTH, append
next numbered session, rewrite NEXT, git add -A/commit, STATUS/OUTCOME.
