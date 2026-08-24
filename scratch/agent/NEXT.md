# NEXT work unit (s2228) — finish expanding the port key-on tuple census

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Make one regeneration-safe diagnostic change in
`../N64Recomp/fixup_game_funcs.py`: raise the per-phase, per-transfer-PC
tuple capacity from 2048 to 8192 everywhere in the s2224 census template.
Keep the tuple fields, phase gates, transfer logging, and all generated game
behavior unchanged. s2226's 2048 arm still overflowed six first-target rings,
so tuple parity remains unmeasured.

Competing hypotheses and the single discriminator:

- H-PortTupleParity: after overflow is removed, the port tuple sets overlap
  the retail sets at the same transfer PC and phase buckets.
- H-PortTupleMismatch: the expanded port sets remain disjoint or materially
  different from retail, identifying an operand/branch-state mismatch rather
  than a logging cap artifact.
- H-TupleCapArtifact: overflow persists, so the port population is still
  hidden and no parity claim is valid.
- H-ExpandedDetailRouteBoundary: the larger diagnostic footprint changes the
  route and loses a required phase despite the positive controls.

The discriminator is one phase-keyed table for all eight transfer PCs at
`0x00696100:640`, `0x00696600:640`, and `0x006AB400:512`, with entry/tail/slot
positive controls, transfer counts, unique-tuple counts, overflow counts, and
set intersection against the s2223 retail table. Reaching all three buckets
with zero overflow and nonzero intersection selects H-PortTupleParity; zero
intersection with zero overflow selects H-PortTupleMismatch; zero overflow
without the later buckets selects H-ExpandedDetailRouteBoundary; continued
overflow selects H-TupleCapArtifact and requires another bounded expansion.
No key-on return, guard, default, or task field may change from this result.

## Exact commands

Before building, verify the existing template and the s2226 result:

~~~sh
rg -n -C 2 'tuples\[8\]\[2048\]|>= 2048ul|tuple_overflow' ../N64Recomp/fixup_game_funcs.py
grep -a '\[m5-keyon-table\]' scratch/s73_post_a_scene/s2226_keyon_tuple_cap/run.log | tail -21
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
recipe; do not run a separate quiet arm in this unit because s2225 proved the
detail toggle fires and s2226 proved the expanded footprint reaches target and
hangar buckets:

~~~sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2228_keyon_tuple_cap 30 12 > scratch/agent/s2228_keyon_tuple_cap_driver.log 2>&1
~~~

Use the resulting `[m5-keyon-table]` rows and phase-keyed transfer tuples only
after the positive controls and all three target buckets are present. Do not
compare stopwatch timestamps or promote the cap change into runtime behavior.
