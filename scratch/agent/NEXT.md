# NEXT (s7484)
HYPOTHESIS-ID: m3-guest-uaf-loads

Item 1a closed s7483. Next idiom class (CURRENT-TRUTH item 1, EH "Not covered: guest LOADS of freed blocks"): class EI,
guest LOADS from freed rs_malloc blocks (use-after-free reads), whole-class, same model as EH.

1. Boring first: does the s7475/s7480 STORE_DIAG hook have a load-side twin? grep src/main/upstream_compat.cpp for s7480_ and
   tools/apply_s7475_slackwatch.py for the store hook emission; check whether the recompiler emits MEM_W/MEM_B reads through a
   hookable macro (N64Recomp output headers in build/ or src/). If no load hook exists, add one behind ROGUESQ_S7484_UAFLOAD=1
   via a fixup script (not a hand edit of generated code).
2. Instrument (one build): on each guest load, test the s7480 freed bitmap; classify with the s7480 locator at load time
   (F = block still free = real UAF read, U/N = re-carved region, Urec = trim defect). Positive control: an in-flight
   premature-free plant that is then READ (ROGUESQ_S7484_PLANT), plus the s7480 locator control.
3. Run tools/s7480_uaf_recipe.zsh-style arms L4/L15 (dd4/dd8), HOLD=220, in one invocation.
Hypotheses: H-load-clean (0 F loads outside the plant) / H-load-uaf (F loads, name the pc + the freeing caller) /
H-load-recarve (all hits U/N, the s7331 scene-reset reader class). Discriminator = locator class of each hit at load time.
If a load hook costs too much frame time to run 220 s, sample (every Nth load) and say so.
