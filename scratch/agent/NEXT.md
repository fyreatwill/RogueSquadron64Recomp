# NEXT work unit (s2226) — expand the port key-on tuple census

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Make one regeneration-safe diagnostic change in
`../N64Recomp/fixup_game_funcs.py`: raise the per-phase, per-transfer-PC
tuple capacity from 256 to 2048 everywhere in the s2224 census template. Keep
the tuple fields, phase gates, transfer logging, and all generated game
behavior unchanged. The 2048 bound is grounded by s2223's independent retail
table, whose largest observed phase-specific set was 1,347 tuples per PC.

Competing hypotheses and the single discriminator:

- H-PortTupleParity: after overflow is removed, the port tuple sets overlap
  the retail sets at the same transfer PC and phase buckets.
- H-PortTupleMismatch: the expanded port sets remain disjoint or materially
  different from retail, identifying an operand/branch-state mismatch rather
  than a logging cap artifact.
- H-TupleCapArtifact: the prior 256 cap hid the relevant port population; the
  expanded run reaches zero overflow and exposes the missing comparison.
- H-ExpandedDetailRouteBoundary: the larger diagnostic footprint changes the
  route and loses a later phase despite the quiet/detail A/B having recovered
  all buckets.

The discriminator is one phase-keyed table for all eight transfer PCs at
`0x00696100:640`, `0x00696600:640`, and `0x006AB400:512`, with entry/tail/slot
positive controls, transfer counts, unique-tuple counts, overflow counts, and
set intersection against the s2223 retail table. Detail reaching all three
buckets with zero overflow and nonzero intersection selects H-PortTupleParity;
zero intersection with zero overflow selects H-PortTupleMismatch; zero
overflow without the later buckets selects H-ExpandedDetailRouteBoundary;
continued overflow selects H-TupleCapArtifact and requires a larger bounded
table before any parity claim. No key-on return, guard, default, or task field
may change from this result alone.

## Exact commands

Before building, verify the existing template and the ground-truth cardinality:

~~~sh
rg -n -C 2 'tuples\[8\]\[256\]|>= 256ul|tuple_overflow' ../N64Recomp/fixup_game_funcs.py
grep -a '\[m5-keyon-table\]' scratch/s73_post_a_scene/s2225_keyon_detail/run.log | tail -21
~~~

Edit only the s2224 tuple-cap constants in `../N64Recomp/fixup_game_funcs.py`,
then regenerate in the required order:

~~~sh
cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp && zsh tools/agent/regen_n64recomp.sh
cd /Users/williambuckley/Documents/Tools/N64Recomp && env python3 fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
~~~

Run the detail arm from the repository root with the existing positive-control
recipe; do not run a separate quiet arm in this unit because s2225 already
proved the detail toggle fires and the route survives its old footprint:

~~~sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2226_keyon_tuple_cap 30 12 > scratch/agent/s2226_keyon_tuple_cap_driver.log 2>&1
~~~

Use the resulting `[m5-keyon-table]` rows and the s2223 retail log only after
the port positive controls and all three phase buckets are present. Keep the
expanded tuple output phase-keyed; do not compare stopwatch timestamps or
promote the cap change into runtime behavior.
