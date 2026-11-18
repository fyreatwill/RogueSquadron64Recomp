# NEXT (s7575)
HYPOTHESIS-ID: do-break-idiom-audit

GUARD-6 closed s7574 (musyx div-trap H-dead, 0 fires / ~721k key-ons, FORCE0 ctl fired). Next: M3-style idiom-class audit of
the 1380 `do_break(` sites still in ../N64Recomp/RecompiledFuncs/funcs_*.c (only musyxKeyOnVoice's 8 were rewritten).
Steps: (1) find what do_break does in the runtime (lib/N64ModernRuntime or src/: abort? log? continue?); (2) script-enumerate
every site with its function, break code (7 = div zero, 6 = overflow, others) and the divisor's defining load (lhu/lbu ->
break 6 statically dead; constant divisor -> both dead); (3) for the remainder, one ungated per-site counter build (like
tools/apply_s7574_keyon_tally.py) plus a forced ctl, run L1 / L4 dd2 / L12 150 s with scratch/s7574/run.zsh as template.
Hypotheses: H-dead (no site fires at defaults), H-live (some site fires: do_break behaviour then decides crash vs silent
divergence; name the writer of the zero divisor), H-static (most sites provably dead offline).
Lesson s7574: phase-gated census helpers read as false zeros at the owner recipe; check gates before trusting a silent census.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
