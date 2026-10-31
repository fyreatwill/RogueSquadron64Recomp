# G1(d): level6 pending-song counter source ownership
HYPOTHESIS-ID: g1-coverage-cd

ONE bounded original-backed extension of tools/g1_dat_inventory.py. s6682
closes the scoped spline-event common prefix (21 records/10 bounded kind7
joins; all counter condition/effect selectors0). Counter90 graph stays open.
No live fallback request, lethal dose, repeat hold, direct stores or win gate.

Hypotheses:
H-typed: pending-song selectors originate in enumerable typed level6 DAT
request records and queue copies preserve the source selector/threshold.
H-derived: a producer transforms or substitutes the selector; qualify the
transform before interpreting the raw DAT descriptor fields.
H-computed: runtime callers/queue producers remain unresolved; preserve exact
open edges, do not claim global absence or fallback safety.
DISCRIMINATOR: trace original readers EDC2C/EDC5C -> globals8010C2F7/F8 ->
writers EE18C/EE1A0 -> descriptor byte2B/word2C -> every producer/copy ->
typed retail sources. Enumerate qualified level6 selectors with owner/kind/
subtype/offset and signed threshold semantics. A nonzero retail control from
this exact family and synthetic90 must traverse the full decoder. Heartbeats
and raw-word searches do not control a missing90 result.

Ground truth and baseline (bounded windows <=60 lines):
    python3 tools/g1_dat_inventory.py --level 6 --check-level6-events --output scratch/agent/s6683_baseline.json
    mips64-elf-objdump -d -j .ovl.mission --start-address=0x800edbb0 --stop-address=0x800edc90 ../rogue_squadron64/build/roguesquadron.elf
    mips64-elf-objdump -d -j .ovl.mission --start-address=0x800ee158 --stop-address=0x800ee1bc ../rogue_squadron64/build/roguesquadron.elf
    rg -n 'c2f7|c2f8|<processPendingSoundCueRequest>|<stageSongFromRequestDescriptor>' scratch/agent/s6681_mission_disasm.txt
Reader uses unsigned selector byte, signed threshold word: nonnegative waits
for count<threshold, negative threshold waits for count>=-threshold; verify
original branch exits before naming polarity. ProcessPendingSoundCueRequest
writes globals from s0+2B/+2C; trace s0 origin and all queue stores/copies,
including resident callers. StageSongFromRequestDescriptor EED7C is only a
lead until its relationship to the actual pending-request owner is proven.

Land checked complete edges and sensitivity/bounds/mutation controls in the
existing tool. Preserve all19 inventories and prior level2..6, safety, script,
event contracts (1399 anchors/1798 mutations in the event contract).
    python3 tools/g1_objective_response_run.py --self-test
Static findings stay static; no runtime/default/lib changes or queued repeats.
If source is not bounded, name that boundary instead of inventing selectors.

Record Session6683, update CURRENT-TRUTH/G1-OBJECTIVE-RESPONSE, rewrite NEXT,
STATUS/OUTCOME, and make a NEW iter commit. No new soak verdicts in s6682.
