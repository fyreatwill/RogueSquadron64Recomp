# G1(d): qualify one named level-3 objective response
HYPOTHESIS-ID: g1-coverage-cd

s6668 closes level2 named loss response: same-owned rescue01 ordinary
2000->1990, one requested1991 dose returns-1, original writer8006594C
counter40 0->1 atVI14690, callback memory/getter1 atVI14694 before flags
109/101. Host SIGSTOP then SIGKILL, no failure/win/progression observed.
All6 manifest hashes match; fixtures/replay/original assertions/build pass.
First rescue01-only run was inconclusive (rescue02 spawned); do not pool it.
No new soak verdict. Default level2 remains ordinary-only. Do not rerun it.

ONE bounded unit: extend the opt-in objective adapter to level3 and qualify
one original-backed named loss/objective counter through accepted damage.
Original ELF/DAT FIRST. Saved level3 TELE firing/writer calls alone do not
prove response. Consult docs/G1-OBJECTIVE-RESPONSE.md level3 row and saved
reconciliation before choosing a target. Keep retail settings; no aim work.

Competing hypotheses:
- H-dose: exact ordinary damage on a named original-backed victim survives;
  one same-owned currentHP+1 request produces the named original death-effect
  counter and callback readback. Select only if both actual writer/readback join.
- H-routing: an exact accepted SEND/health control works but death effect
  differs from the callback-relevant contract. Original branch/effect trace
  plus full node/NPC/descriptor/actor/projectile/seq join distinguishes it.
- H-observation: actual named store occurs but callback monitor/getter misses
  it. Compare actual store, memory readback and original getter return, with
  changing-value controls; a heartbeat is insufficient.
Discriminator is the WHOLE chain in one build/one flight, ordinary then at
most one same-actor dose if necessary and original end ordering allows a
safe stop. Each absence without positive control is inconclusive. Do not
add a field per iteration or count an unsupported null as coverage.

Starting commands (repo root):
    mkdir -p scratch/agent/s6669_lvl3_response
    python3 tools/g1_dat_inventory.py --level 3 --output scratch/agent/s6669_lvl3_response/original.json
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80102D08 0x80103108 > scratch/agent/s6669_lvl3_response/callback.txt
    rg -n 'lv3_checkComplexObjectives|rs6661_target|rs6664_transport_common|rs6668_counter_return|rs6660_selected' tools/apply_s6657_objective_response.py ../N64Recomp/RecompiledFuncs/funcs_44.c
    rg -n 'Level 3|level.?3|lvl3' docs/G1-OBJECTIVE-RESPONSE.md tools/g1_objective_evidence.py
Read bounded callback windows, then follow original calls/branches through
counter meaning, victim death effect and failure/end flags. Inventory parser
layouts are hypotheses until their original consumer instructions match.
Do not assume level2's descriptors, handlers, counters or addresses apply.

Before building, record chosen original target/counter and end ordering here.
Extend adapter and runner choices to3, select only proven owned typed victims,
carry existing mark-all, changing-value, force/SEND/health/effect/store/
readback/getter table in one build. Add full positive/negative analyzer
fixtures (identity, no ordinary control, missing store/getter, duplicate dose).
Persist generated edits via fixup tooling. Only if required, regeneration
order is make_elf -> N64Recomp -> fixup_game_funcs -> cmake.
    python3 tools/g1_objective_response_run.py --self-test
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
After extending runner, unlocked screen and no existing game process:
    env ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1 python3 tools/g1_objective_response_run.py s6669_response --level 3
Use the shortest ORIGINAL-backed activation window; change runner budget
only if original activation requires it. If a named positive counter is a
failure gate, stop after its original getter with host SIGSTOP before the
branch; do not suppress or resume guest failure. Inhibit all further forces
at the dose. SIGKILL the process group promptly on done; post-SIGSTOP stalls
are harness artifacts. Do not write health/counters/Booleans/timers directly,
select arbitrary victims, or test success/progression.

One flight, same-run phases keyed by VI/activation; no animating cross-run
A/B. Check manifest env/source/binary hashes, retain source at launch if
changed later, and report all arms, controls and missing evidence honestly.
Update objective table/CURRENT-TRUTH, append next numbered ledger entry,
rewrite NEXT, git add -A/commit, STATUS and OUTCOME. No lib edits expected;
if needed, export submodule patches in the same iteration.
