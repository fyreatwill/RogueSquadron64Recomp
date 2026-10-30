# Level-2 typed objective-target ownership
HYPOTHESIS-ID: g1-coverage-cd

s6662 lands level2 ordinary-only adapter and completes one clean flight,
VI5080..10483,169.97s. Zero forces: no sampled descriptor passes count40
selection; mark-all eligibility controls5/13/10, counter changes8, Boolean
changes7. Do NOT repeat that recipe. Its census is untyped and every arm
saturates candidate4096. No claim that the mission lacks a loss target.

ONE bounded ownership/census correction, grounded in original game code,
with one validation flight only after the full table can discriminate.
No lethal level2 dose, direct state writes, success/failure, aim or progression.

Competing hypotheses:
- H-kind: relevant target is in the object table under a different node kind
  or descriptor path. Original producer/consumer loads and a typed same-flight
  descriptor join select it; fix the join, do not guard the target away.
- H-late: correct kind/path, but the target arrives after the old candidate
  budget is exhausted or between census samples. Persistent spawn/retire
  records plus phase-scoped relevant-row logging select late availability.
- H-absent: original level2 setup/script legitimately does not instantiate
  a counter40 target in the measured first-flight window. Original spawn
  conditions AND a complete typed table with a selected-target detection
  positive control are both required; an untyped zero never selects this.

Discriminator: one table keyed by node kind, slot/generation, NPC, descriptor,
objective counter/Boolean payload, birth/retirement VI, candidate/accepted
SEND and health actor. Establish original node-kind and table-bound rules
first. Log all relevant transitions, not4096 arbitrary early shape rows.
Preserve mark-all controls and actual changing-value readbacks in the same
phase. If no safe relevant target exists, land the complete ownership
correction and report the proved boundary; never infer response failure.

Ground truth first (fresh paths; bounded reads):
    mkdir -p scratch/agent/s6663_lvl2_owner
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80101CD0 0x80101EF4 > scratch/agent/s6663_lvl2_owner/init_elf.txt
    rg -n 'jal|lw|lhu|sw' scratch/agent/s6663_lvl2_owner/init_elf.txt
    rg -n 'lv2_initializeObjectTracking|lv2_checkComplexObjectives|lv2_calculateFriendliesSaved' syms/rogue_squadron.syms.toml
    rg -n '80130BB0|80130BB4|80130BB8|rs5841_cand' tools/apply_s5812_npc_spawn_class.py tools/apply_s5813_npc_fate.py tools/apply_s6657_objective_response.py
Read original functions called by the initializer and the table's actual
producer/consumer in <=60-line windows; use original ELF rather than host
census as witness. Read s6662 population.json and final response.json with
computed summaries, never cat the log. All7 manifest hashes matched.

Edit tools/apply_s6657_objective_response.py and the complete analyzer together;
fixup replay already includes the adapter. Write final targets, original
ownership rules, all controls and stop gates here BEFORE build. Preserve
level0/1 and ordinary default TELE. Then:
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    python3 tools/g1_objective_response_run.py s6663_owner --level 2
Fresh capture, unlocked screen, build/ROM, SIGKILL watchdog. No lib edits or
full fixup of an existing tree. Ordinary damage only, stop on first named
changing store and finish readback; no intentional end gate.

Previous artifacts: scratch/agent/m6/g1_lvl2s6662_lvl2_final/ and
scratch/agent/s6662_lvl2/{population.json,*_elf.txt,helper_control.log,
level1_control.log}. g1_lvl2s6662_lvl2 is an incomplete DIFFERENT build;
never overwrite or pool it. No queued-soak additions.
