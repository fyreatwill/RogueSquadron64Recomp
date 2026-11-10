# NEXT: owner reports first; otherwise fix the N64Recomp self-branch miscompile (engineering rung)
HYPOTHESIS-ID: n64recomp-selfbranch-fix
Context: misnomer-rename thread CLOSED s7080 (do NOT do more renames; s7077-s7080 were rename-only and the loop's
no-engineering counter is high). Known miscompile (PROJECT-OVERVIEW "Silent N64Recomp miscompile", PORTING-STATE s6871
design, s6878 H-dead on missions 1-2): 16 backward branches that leave their function are emitted as a jump to the
function's OWN entry instead of the real target, in the voice resampler helpers (0x8009264C..0x800934A4 area).
Unit (one bounded change):
1. Enumerate the 16 sites from the N64Recomp "branching outside" warnings / s6871 scan; for each, record source fn,
   branch PC, real target, the function containing the target.
2. Hypotheses: H-tail (target is the start of a loop body that can be reached by calling the containing function at a
   label -> emit a correct goto inside a merged function) vs H-dup (simplest correct fix: in a new tools/fixup_selfbranch.py,
   replace each bad `goto <own entry>` with a call to a helper that runs the target block, or make N64Recomp treat the
   pair as one function via syms toml size merge) vs H-abort (if neither is safe, replace with a loud trap + log so a
   live hit can never silently corrupt). Pick the smallest CORRECT one; H-abort is the floor.
3. Discriminating control: unit-test the patched C for one site with a synthetic rdram/ctx (or an ASan/separate build dir
   arm that forces the branch), plus the usual: fixup_preempt_point.py says 6, cmake build, L6 boot to flight clean
   (sed s7080->s7081 scratch/s7080/run.zsh).
Regen order if regen is needed: make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake (docs/REGEN-VERIFY.md: live tree
is not regenerated; prefer a fixup applied to the live tree, idempotent, also wired into the fixup chain).
