# NEXT: level-0 forced-route counter1 response in one flight
HYPOTHESIS-ID: g1-coverage-cd

One bounded engineering experiment: adapt the existing ROGUESQ_TELE_BOLT
lever to off/on/off windows inside ONE forced-level-0 flight, and join
forced intersection -> victim -> actual DAT counter write. No wins,
progression, aim/steer tuning, repeat holds or cross-run animated A/B.

Hypotheses:
- H-response: forced intersections reach the named counter1 writer and
  yield nonzero before/after changes with victim attribution in that flight.
- H-incidental: the attributed writes are only counter2/failure or Boolean
  activity, or counter1 moves without attribution to the forced victim.
- H-wrong-route/control: selector/callback identity or the hit/value-change
  positive control is absent; the result is unevaluated, never a null.

Discriminator: a single event table keyed by explicit flight epoch and VI,
arm off/on/off, victim object+descriptor, counter index, actual old/new,
writer PC and callback level. A victim-linked nonzero counter1 delta in
on selects H-response; only counter2/different state selects H-incidental;
missing identity or no live value-detector control selects H-wrong-route.
Arm rate differences alone cannot prove causality on an animating scene.
No mission completion is required. Stop at counter1 >= 18 or counter2 >= 1
(or 90 flight seconds), before an objective end threshold; do not poke wins.

Ground truth / boring checks BEFORE instrumentation:
    python3 tools/g1_objective_evidence.py --check > scratch/agent/objectives_before.md
    sed -n '1,105p' docs/G1-OBJECTIVE-RESPONSE.md
    sed -n '1,100p' docs/M6-OBJECTIVE-COUNTER-WRITERS.md
    sed -n '1,100p' tools/apply_s5809_ctr1_log.py
    sed -n '1,130p' tools/apply_s5835_sphere_probe.py
    rg -n 'elf_path|output_func_path' rogue_squadron.toml
Read original ELF instructions at the DAT writer and lv0 gate with
`python3 tools/disasm_mips_elf.py <elf_path> <start> <stop>` (<=60 lines
per output), rather than relying only on our generated instrumentation.
Read docs/debug-trace-env-vars.md before adding logging. Existing retail
oracle is undriven in missions; a boot-only null cannot settle this test.

Existing exact lever: ROGUESQ_TELE_BOLT=1 changes the tested segment at
intersectSegmentWithObjectSphere, tools/apply_s5835_sphere_probe.py.
It is cached at run start and currently lacks in-run switching. Add one
opt-in diagnostic adapter there; do not claim the windows already exist.
Use committed VI origin/width and count, exported by host helpers, to gate
on first selected mission at origin 0x00690400 or 0x00620400, width512.
PROBE_PHASE_WIDTH=512 / PROBE_KEYS_FROM_PHASE=1 gates the route autopilot,
NOT the measurement: the hangar also has width512. Confirm selector B40=0
and lv0_checkComplexObjectives before accepting the flight. Use e.g.
0..299 VIs off, 300..599 on, >=600 off; stop earlier at the counter limit.
Reset log/value-control budgets per flight epoch. Batch all joins and a
changing-value positive control in this same build. Record real old/new
at the writer; ctr1/setter call counts and heartbeat are insufficient.

Persist generated diagnostics in fixup scripts, apply them to live output,
then build once:
    cmake --build build --target RogueSquadron64Recomp -j5
If full regeneration is needed, obey make_elf.py -> N64Recomp ->
fixup_game_funcs.py -> cmake; do not partially regenerate a source tree.

Base existing route (run only AFTER the diagnostic adapter is installed,
using a fresh tag so saved logs are not overwritten):
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    env ROGUESQ_TELE_BOLT=1 ROGUESQ_LOG_HITS=1 LEVEL=0 TAG_SUFFIX=s6657_response HOLD_S=150 zsh scratch/agent/g1_level_coverage_common.zsh
This exports FORCE_SAVE_MISSION=0, FORCE_UNLOCK=0, NO_SAVE_WRITE=1,
LOG_OBJBOOL=1, LOG_HUDBIT=1; m6_god_common.sh runs from build with ROM,
watchdogs and SIGKILLs. Install a stop-on-response condition in the
experiment wrapper; the old runner otherwise waits a fixed 130s verify.
Off/on/off instrumentation needs an explicit new opt-in, recorded in
NEXT.md before running. Defaults and ordinary TELE behavior stay unchanged.

First missing witness was selected because g1_lvl0ctl/tele are absent;
legacy s5843/s5844/s5845 do name lv0 and show c1 activity but use the old
route. lvl10–18 also have no saved ctl/tele pairs. Do not revive the old
lvl6 "valid null" (heartbeat only) or transfer lv0 id2 semantics to lvl7.
