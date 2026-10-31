# G1(d): level6 typed-script ownership before counter90 safety
HYPOTHESIS-ID: g1-coverage-cd

ONE bounded original-backed extension of tools/g1_dat_inventory.py. s6680
recovers the complete c50->Boolean99->counter99->Boolean11/Bit8 control and
proves FFFF API10 eagerly increments50/90 while HP500->490. It does not prove
counter90 unused or admit a live fallback request. s6679 Barracks is still
unregistered; do not repeat its admission hold. No damage/lethal/run unit here.

Hypotheses:
H-DAT: resolveScriptedNameTokenList's owner at effect-context+24 is a bounded
retail DAT record; opcode3 counter selectors can be enumerated for level6.
H-derived: constructor copies/transforms another source; raw level6 DAT-word
search cannot establish the selectors. Trace the original transform first.
H-computed: owner/record extent or selected targets remain runtime-dependent;
retain the exact unresolved constructor/edge, not an absent90 conclusion.
DISCRIMINATOR: original constructor -> context+24 -> record+50 count and
record+54/58/5c stride16 -> opcode3 -> selected DAT name join, checked against
retail bytes and original opcode semantics. A typed nonzero counter case in
this script family (another level if necessary) is the positive control; a raw
float90 hit or function-entry count is not. Enumerate EVERY level6 record only
when its owner and bounds are proven. Unresolved target effects remain explicit.

Ground truth and regression baseline first:
    python3 tools/g1_dat_inventory.py --level 6 --check-level6-safety --mutation-check-level6-safety --output scratch/agent/s6681_baseline.json
    mips64-elf-objdump -d -j .ovl.mission ../rogue_squadron64/build/roguesquadron.elf > scratch/agent/s6681_mission_disasm.txt
    rg -n 'jal.*800f410c|jal.*800f3290|<executeActorType1Effect>|<resolveScriptedNameTokenList>' scratch/agent/s6681_mission_disasm.txt
    mips64-elf-objdump -d -j .ovl.mission --start-address=0x800f410c --stop-address=0x800f41a0 ../rogue_squadron64/build/roguesquadron.elf
    mips64-elf-objdump -d -j .ovl.mission --start-address=0x800f3290 --stop-address=0x800f3320 ../rogue_squadron64/build/roguesquadron.elf
    mips64-elf-objdump -d -j .ovl.mission --start-address=0x800f3480 --stop-address=0x800f34b8 ../rogue_squadron64/build/roguesquadron.elf
    rg -n 'executeActorType1Effect|resolveScriptedNameTokenList|Effect' ../rogue_squadron64/symbol_files/mission_overlay.txt
Read <=60-line windows; never the whole ledger. Table800A8A20 opcode3 points
F339C; F33BC reads counter trunc.w.s(record+58+16*i), threshold+5C. Caller
F439C passes s5 effect context; F32D8 loads context+24. Follow that context's
original constructor and DAT relocation contract. Do not confuse NPC subtype3B
(troopers) with the script opcode or assume DAT tables share layouts.

Land checked typed ownership/record edges and mutation negatives in the
existing tool, preserving all19 inventories and level2..6 prior contracts.
Current validations: safety996 anchors/1048 rejected mutations,30 base candidates,
167 typed condition rows (not scripts),125 direct getters; both scoped reader
sets contain no90. They are NOT a complete consumer graph. Original integer
slice uses recorded presentation/audio stubs and is same-source evidence.
Run analyzer self-tests too:
    python3 tools/g1_objective_response_run.py --self-test
No runtime build, lib/default edits, fallback request, win/progression or queued
repeat soak. If this ownership edge resolves, select the next actual computed
consumer edge; do not authorize a dose on the strength of a scoped null.

Record Session6681, CURRENT-TRUTH and G1-OBJECTIVE-RESPONSE, rewrite NEXT for
one unit, STATUS/OUTCOME and a NEW iter commit. No new queued-soak verdicts in
s6680. s6680_validation.json records all19 unchanged inventories, prior-contract
regressions and checker controls; s6680_safety.json holds the full typed graph.
