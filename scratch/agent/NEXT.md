# Level-1 descriptor-targeted loss-counter response
HYPOTHESIS-ID: g1-coverage-cd

s6659 completed the generalized adapter and one corrected flight. Do not
repeat the generic recipe: it produced two complete id10 chains, no named
13/40/41 response. No win/progression/aim/steering work. No repeat holds.

Read CURRENT-TRUTH, this file, SOAK-RESULTS tail in that order; wc -c first.
Maintenance threshold is60000. Current iteration did not trigger it.

One bounded change + ONE selected-level1 flight: target forced collision
candidates whose actual NPC descriptor declares counter13/40/41, preserving
the existing off/on/off and exact identity table. Stop at the FIRST live
named loss-counter response (including its readback), far below id13>=5.
Default behavior remains retail. Do not force completion/Boolean6.

Hypotheses:
- H-response: a descriptor-selected victim reaches accepted SEND, actual
  counter writer and callback readback for13/40/41. It is a loss response,
  not successful progress; original ELF proves the semantics.
- H-victim-selection: relevant live NPC descriptors exist but are absent
  from the collision candidate population or rejected before the lever.
- H-effect: relevant forced candidates receive accepted SEND, but do not
  invoke their descriptor's objective counter writer within the measured
  flight. This is a limited no-response result, not proof of broken logic.

Discriminator, ONE instrument/build/run: per-arm live NPC descriptor census
with index/delta and Boolean fields, candidate eligibility and rejection
reason, force shape/projectile/node/NPC/descriptor, accepted SEND, actual
store PC/id/old/new and callback readback. Include a mark-all ELIGIBILITY
control that visibly labels the known id10 candidates in this SAME run;
keep actual changing counter values as the independent detection control.
A live-target/candidate population split selects H-victim-selection; a
complete named chain selects H-response; accepted named hits without their
writer select H-effect only with all controls firing. Missing target/control
means unknown. Do not spend another iteration threading one join field.

Ground truth BEFORE instrumentation:
    sed -n '150,245p' docs/G1-OBJECTIVE-RESPONSE.md
    cat scratch/agent/s6659_response/lv1_friendlies_elf.txt
    cat scratch/agent/s6659_response/lv1_callback_elf.txt
    cat scratch/agent/s6657_response/destruction_elf.txt
    rg -n 'rs5841_cand|rs5837_en &&|rs6657_gate|rs6657_force' tools/apply_s5835_sphere_probe.py tools/apply_s6657_objective_response.py
    sed -n '1,210p' tools/apply_s6657_objective_response.py
    sed -n '1,165p' tools/g1_objective_response_run.py
    sed -n '28,39p' docs/debug-trace-env-vars.md
Verify descriptor offsets/field meaning with original ELF, <=60 lines per
window, before filtering. node+4->NPC; NPC+0x34->descriptor. Do not mistake
SEND cls13 for a proven counter13 target without the original load chain.
Use tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf.
Counter13 at80138090; 40 at801380FC;41 at80138100; Boolean6 at801388A5.
Friendlies-saved=19-(40+13+41); c13>=5 fails, Boolean6==1 completes.

All generated hooks go in persistent adapter/fixup replay. The s5857 health
helper was FIXED this iteration: unsigned C arithmetic manufactured a4GiB
host offset. Do not restore the old expression or add a guest-pointer guard.
Reproduction/ELF/control evidence: scratch/agent/s6659_response/.
Adapter/health replay stability passed six checks. Do not run full fixup on
the existing tree. If regeneration is needed: make_elf -> N64Recomp ->
fixup_game_funcs -> cmake. Preserve lib worktrees.

After implementing the entire discriminator and writing the exact selected
counter stop/positive-control design here, use:
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    python3 tools/g1_objective_response_run.py s6660_targeted --level 1
    python3 tools/g1_objective_response_run.py s6660_targeted --level 1 --analyze
Screen must be unlocked. Runner uses a fresh path, binary/source/env
manifest, 360s hard timeout, SIGKILL recipe group on done/crash. Run from
build with ROM via existing recipe. No queued repeat soak needed.

Preserved s6659 evidence:
- g1_lvl1s6659_response/: one host diagnostic SIGSEGV before TELE-on,
  rs5857_hp+212, far400319130; first flight is not a behavioral arm.
- g1_lvl1s6659_response_v2/:176.59s, VI5271..10674,25 forces,0 crashes,
  id10 0->4->8->8,8 live readbacks; two exact incidental chains seq14/17.
  ids13/40/41 and Boolean6 stay0. No full VERIFIED promotion.
- response.json records final analyzer hash; launch manifest preserves the
  earlier analyzer version. Neither log was overwritten. Dynamic chain
  causality remains single-source; original ELF supplies independent
  semantic/address-calculation constraints, not retail equivalence.
