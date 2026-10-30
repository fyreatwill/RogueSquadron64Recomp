# Locate level-2 count40's original producer and spawn boundary
HYPOTHESIS-ID: g1-coverage-cd

s6664 CLOSED the captured handler-map correction. All23 s6663 kinds plus
2 late s6664 kinds are original-classified: four ordinary objective-damage
handlers, twenty excluded handlers, one DAT spawn trigger. Ground transport
is also supported from earlier work, but not observed. Do not repeat the
map flight or start a one-handler-per-session audit. Report:
docs/G1-OBJECTIVE-RESPONSE.md, s6664 section. Actual capture adapter preserved
at scratch/agent/s6664_lvl2_kinds/captured_adapter.py; final adapter additionally
classifies the two late message5-ineligible kinds (built/fixtures only).

One flight VI4955..10356,171.81s,0 crash/force. Mark-all15/17/16, three local
selector fixtures, six changing counters and ten real natural health
reductions. No count40 descriptor/candidate in the observed population.
This is NOT target absence: cleared birth/retirement descriptors and later
script spawns remain possible. No forced count40 health response established.
Original ECE10 descriptor is payload+0, with +70 a spawn limit; never read
it as a death-objective tuple. D5208 subevent12 has separate +B0 fields.

ONE bounded work unit: identify the ORIGINAL producer/activation condition
for level2 count40, or establish a complete original-backed DAT inventory
that separates definition, activation and damage-object ownership. Prefer
original data/ELF evidence before a new instrument. Do not reuse the old
runtime census as ground truth or simply hold longer waiting for luck.

Competing hypotheses:
- H-definition: the forced level2 route loads no count40 death descriptor
  (wrong data identity or count40 is written by a distinct script). A complete
  decoded level-DAT inventory plus original callback/writer semantics splits it.
- H-activation: a count40 descriptor exists, but original spawn conditions
  keep it inactive during this route. Join its definition to original gating
  Boolean/counter/trigger reads and actual parent/spawn/child identities.
- H-layout: count40 belongs to another original descriptor layout or writer
  (e.g. scripted trigger, special debris event), rather than ordinary +70
  death fields. Establish the real producer/consumer before interpreting it.

Discriminator: ONE full table of level-DAT definitions (type/name, validated
layout, objective fields), activation predicates, original spawn dispatch,
actual child ownership and observed counter writer. A complete inventory
without40 selects a data/script boundary only after positive-control known
D5208 descriptor id71 is decoded correctly. A40 definition with an unmet
original predicate selects activation; a different original field/writer
selects layout. If dynamic capture is required, collect all table joins in
ONE build/run, phase-scoped, including a mark-all dump that visibly contains
known live descriptor addresses from the same run. Do not add one field or
repeat a sparse census. Unknown data/layout cannot support a null.

Start commands (bounded windows <=60 lines; no whole logs/ledger):
    mkdir -p scratch/agent/s6665_lvl2_producer
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80046620 0x80046784 > scratch/agent/s6665_lvl2_producer/parse.txt
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800656B4 0x80065A5C > scratch/agent/s6665_lvl2_producer/spawn_effect.txt
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80047B48 0x80047B70 > scratch/agent/s6665_lvl2_producer/lookup.txt
    rg -n 'jal|112\(|116\(|120\(|124\(|128\(|132\(' scratch/agent/s6665_lvl2_producer/*.txt
    rg -n 'DAT|dat|decompress|inflate|manifest' ../rogue_squadron64/docs/data_blob/extract_assets.c
    sed -n '1,60p' tools/dump_lv0_objective_targets.py
    rg -n 'getLevelDatItemByName|spawnDatStructureNpcByType|parseDatItemCommon|applyDatObjectiveTriggerEffect' syms/rogue_squadron.syms.toml
Original level2 initializer already disassembled:
    scratch/agent/s6664_lvl2_kinds/level2_init.txt
Its C7830 calls register objective handles, not proof of actual spawn.
Read complete parser/subtype definitions needed to validate DAT offsets.
The actual run and full live/candidate/SEND/health/store rows remain:
    scratch/agent/m6/g1_lvl2s6664_kinds/response.json
    scratch/agent/s6664_lvl2_kinds/summary.json

Before building rewrite this file with the proven data source/table and
outcome interpretation. No arbitrary victim, lethal level2 dose, direct
health/counter write, aim/steering, win or mission progression. Keep default
and level0/1 behavior. If warranted, use fresh paths and existing runner:
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    python3 tools/g1_objective_response_run.py s6665_producer --level 2
No new repeat soaks. Check maintenance threshold first; CURRENT-TRUTH was
59505 bytes at the s6664 update, below60000.
