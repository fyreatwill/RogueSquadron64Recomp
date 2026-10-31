# G1(d): level6 spline-event remap and counter reader ownership
HYPOTHESIS-ID: g1-coverage-cd

ONE bounded original-backed extension of tools/g1_dat_inventory.py. s6681
closed kind3/subtype3 inline scripts statically:21 records/168 slots, no op3;
completion selectors0. Context24 constructor source and fixed8 bounds proven.
No live fallback request, lethal dose, repeat hold, stores or win gate.

Hypotheses:
H-typed: spline event stride8 + remap points into bounded level6 DAT kind7
records; condition counter+2C and effect counter+34 can be enumerated.
H-derived: remap/relocation transforms another source; prove that transform
before reading raw selectors or asserting a missing90.
H-computed: owner/index bounds depend on runtime state or unresolved kinds;
retain the precise edge and do not claim absence or fallback safety.
DISCRIMINATOR: original F4660..46AC source+28 count/+2C event array, event+6
index, source+D8 remap at source+D4+value, remap+2 index -> DAT header3C kind7
table -> F3CB0 a1 -> F3D28 counter read (+2C selector/+30 threshold) and
F3D74 read/modify/write (+34 selector/+38 delta). Join every selected level6
event to its typed record. A retail nonzero selector in this exact family
(other level if needed) plus synthetic90 and bound violations controls the
whole decoder. Function-entry/heartbeat or raw float90 is not a control.

Ground truth/regression baseline:
    python3 tools/g1_dat_inventory.py --level 6 --check-level6-scripts --output scratch/agent/s6682_baseline.json
    mips64-elf-objdump -d -j .ovl.mission --start-address=0x800f4648 --stop-address=0x800f46f4 ../rogue_squadron64/build/roguesquadron.elf
    mips64-elf-objdump -d -j .ovl.mission --start-address=0x800f3cb0 --stop-address=0x800f3d84 ../rogue_squadron64/build/roguesquadron.elf
    rg -n 'jal.*800f3cb0' scratch/agent/s6681_mission_disasm.txt
    rg -n 'case 7|unk3C|unk34|unk38' ../rogue_squadron64/docs/dat_files/load_level_dat.c
Read <=60-line windows. Follow original DAT kind7 relocation and subtype
semantics before decoding fields; do not assume all events share layouts.
Original s6681_*.json are static evidence, not live/hardware witnesses.

Land complete checked record edges and sensitivity/mutation controls in the
existing tool, preserving all19 inventories and level2..6 prior contracts.
Current script check1282 anchors/1502 rejected mutations. Both old safety and
script checks retain unresolved NPC/actor/radar/music/handle and alias edges.
    python3 tools/g1_objective_response_run.py --self-test
No runtime build, lib/default changes or queued repeat soak. Close this family
only when ownership/bounds and positive control qualify; scoped missing90
never admits a fallback hit because eager c50 coupling already exists.

Record Session6682, CURRENT-TRUTH and G1-OBJECTIVE-RESPONSE, rewrite NEXT for
one unit, STATUS/OUTCOME and a NEW iter commit. No new soaks in s6681.
