# NEXT: attribute the runtime writer of voice 0x801724C0 +0x34
HYPOTHESIS-ID: m5-audio-destub

s4596 completed the static census; see docs/M5-S4596-VOICE34-CENSUS.md.
The only relevant voice-field writers are 0x800921E8 (sample descriptor +4)
and 0x80090C80 (source voice +0x38). At 0x800903F0, a3 is a direct load of
voice +0x34 and a1 is only that value plus an aligned offset. This selects
H-writer/input over H-builder. Retail independently showed B0xxxxxx pointer
stores, so the port's ASCII value remains illegitimate.

Next work unit: build a complete phase-scoped port store census for physical
0x1724F4, covering every generated store site or the central RDRAM write path.
The retail positive control is already recorded: whole-RDRAM 10,004 writes and
four target writes from 0x80007670. Competing hypotheses: (H-init/keyon) the
port target write is from 0x800921E8 or 0x80090C80; (H-foreign) it is from a
different guest PC; (H-host) no guest store occurs and the value enters through
host/translation state. The discriminating measurement is the first target
write's PC, value, and phase, with an adjacent-range port store control firing
in the same target phase. The s4597 phase control fired, but its direct
rs_strncpy entry and target rows were zero; do not treat that as a complete
no-store result until the new census has a store control. Do not add a
mitigation. Exact work sequence: extend or replace
`tools/apply_s4597_target_store.py` so the complete generated-store census is
regeneration-preserved; run `cmake --build build --config Debug --target
RogueSquadron64Recomp`; then run from `build/` with
`ROGUESQ_NODEFAULT=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1`, the repeated-Start late
route, and phase/store logging enabled. Expected split: init/keyon PC,
foreign guest PC, or host/no guest store, each valid only if the adjacent
store control fires at `640/0x006A2900`.
