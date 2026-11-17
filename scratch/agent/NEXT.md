# NEXT (s7506)
HYPOTHESIS-ID: bz-jr-slotorder-latent

Fold first: SOAK-RESULTS line for s7505_fc_levels (rows `tag=s7505_fc_levels fc arm=` in scratch/s7505_fc_levels/out.txt). Pass = fc
score 0 (ctl ok, no BAD= list) -> FC CLOSED 6 levels and the m3-partition-over-live-block series stays closed. A BAD= episode on a lit
frame (ml>0.05) or shown>2 swaps is new: read the `[s7505] ep` row, name the block owner (s7475 record ra) before anything else.
(fb score 5 inside that soak is expected: the FB present-path rows.)

Work unit (ITERATION 3c / CURRENT-TRUTH item 20: the heap series is closed; bounded engineering, not a census): fix the LATENT generator
defect found by class BZ s7416 (PORTING-STATE line ~196354): N64Recomp emits a jr/jalr delay slot BEFORE `LOOKUP_FUNC(ctx->rS)`, but MIPS
reads rS before the slot. 2 known sites, both in dead data_gap_80024A0C (jr $v0 with negu/ori $v0 in the slot).
Hypotheses: H-fix-local (latching rS into a temp before the slot changes ONLY those 2 sites' emitted C; every other function
byte-identical) / H-fix-wide (the latch changes other emission, e.g. register-allocated jump-table jr: then restrict to slots that write rS).
Steps: 1) find the jr/jalr emission in /Users/williambuckley/Documents/Tools/N64Recomp (grep LOOKUP_FUNC / process_instruction jr); emit
`gpr jr_target = ctx->rS;` before the slot only when the slot writes rS (keeps all other output identical). 2) Regen in order make_elf.py ->
N64Recomp -> fixup_game_funcs.py -> cmake into a scratch output, then tools/s7421_regen_drift.py <live> <regen> <compare.json> --control:
the diff must be exactly the 2 data_gap_80024A0C sites. 3) Re-run tools/s7416 BZ tool --controls (hazard count must drop to 0, mutant
control still caught). 4) Build + one L4 300 s hold. Commit the N64Recomp change (it is its own repo: commit there too, note the hash).
