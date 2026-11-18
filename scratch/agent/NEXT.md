# NEXT (s7559)
HYPOTHESIS-ID: regen-fidelity-drift

GR CLOSED s7558 (tools/s7558_gr_census.py --check rc 0, controls 16/16; 1 BEHAV = B40 gate default 0 vs s4701 pass-through,
owner decision, A/B soak scratch/agent/soak_queue/s7558_b40_ab.sh queued: fold it if SOAK-RESULTS has it).
s7558 also repaired the regen chain (rs64_anchor.py: 6 fixups broke on s7484 load wraps). Remaining regen health (CURRENT-TRUTH 19b):

Unit: classify the regen-vs-live drift. Trees: scratch/s7558/{pristine,renamed,replay,verify} exist (rebuild per 19b if gone).
  tools/regen_verify.sh scratch/s7558/replay scratch/s7558/verify   -> 2607 same / 141 differ / 18 only-live / funcs_50.c live-only
  s6870 baseline (docs/REGEN-VERIFY.md): 2688 / 78 / 17 (the 78 listed in scratch/s6864/cmp2.json if present, else REGEN-VERIFY).
Per differing function NOT in the baseline: source diff replay vs live (normalise whitespace + reorder of file-scope blocks), then
Hypotheses: H-layout (source equal modulo moved file-scope helpers / static order; object diff from branch offsets only) /
H-missing-step (live carries a PATCH tag no replay step emits: name the tag, add the apply script to the vendored list) /
H-live-handedit (live text no script produces and no tag: decide keep -> write a fixup, or drop) / H-replay-extra (replay emits a
block live lacks). Discriminator: the tag set difference per function (grep -o 'PATCH: s[0-9]+' live vs replay) + the
normalised-source equality. Controls: plant one removed PATCH line in a copy of a live file -> H-missing-step; a pure block
move -> H-layout. funcs_50.c (live-only file) and the 18 only-live functions get the same treatment.
Then (b) of 19b: the s7363/s7364/s7366 host-code census debt (verdict rows) so regen_replay.sh runs to "ok".
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
