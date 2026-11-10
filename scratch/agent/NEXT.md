# NEXT: owner reports first; otherwise ladder item 4 (generated-symbol renaming sweep)
HYPOTHESIS-ID: generated-symbol-renaming-sweep
Context (s7070): gfx-hash-audit closed (RT64 framebuffer tracking, ~0.22 ms/frame, no rs64 caller). Every CURRENT-TRUTH
Next-steps item 1-12 awaits the owner's flight/look; 13/13b closed; 14-15 parked. AN OWNER REPORT PREEMPTS THIS.
If none: check `grep -n '^## Session ' PORTING-STATE.md | tail -15` (ITERATION.md item 4 REVISIT rule), then resume
the renaming sweep: count remaining `func_0x` placeholders, pick the next contiguous address band, name from
call-graph/string/caller evidence. Beware: rename edits do not reset the churn counter — pair them with a real
code/tool change (e.g. a tools/ helper that ranks unnamed functions by host self-time from the s7069 dumps, so the
sweep names the hot ones first).
Hypotheses for the ranking pass: H-hot-named (top guest self-time functions are already named) vs H-hot-unnamed
(several hot guest functions are still func_0x...). Discriminator: tools/s7067_selftime.py --thread Game over
scratch/s7069/on, joined with the rename map.
