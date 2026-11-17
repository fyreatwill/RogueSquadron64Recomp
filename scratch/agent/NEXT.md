# NEXT (s7558)
HYPOTHESIS-ID: class-gr-unconditional-fixups

GQ CLOSED s7557 (tools/s7557_gq_census.py rc 0, controls 11/11): 115 default-on env levers, all with =0; 17 undocumented ones now in
generated docs/DEFAULT-ON-LEVERS.md. GQ could not see behaviour changes made with NO env read: GR asks about those.
Static census, tools/s7558_gr_census.py:
- enumerate every apply_*.py / fixup_*.py step that the regen actually runs (fixup_game_funcs_vendored.py list + the standalone
  fixup_*.py called by the regen) and the `/* PATCH: ... */` blocks they emit into ../N64Recomp/RecompiledFuncs/*.c; mark each
  emitted block gated (contains a getenv / references a gated helper) or ungated.
- classify every UNGATED block: recompiler-correctness (restores retail semantics N64Recomp got wrong: delay slot, label realign,
  movz/movn, selfbranch, dupcall, jump tables - retail-preserving, no switch needed), host-runtime plumbing (call into a host
  replacement with the same contract), or game-behaviour change (alters what retail would do: guard, clamp, skip, value repair).
- join each game-behaviour block with docs (DEFAULT-ON-LEVERS, OWNER-OPT-INS, CURRENT-TRUTH, PROJECT-OVERVIEW) and PORTING-STATE.
Hypotheses: H-correctness-only (every ungated block is retail-preserving) / H-hidden-change (an ungated game-behaviour change: list
it; add a ROGUESQ_<NAME>=0 switch in its apply script only if the owner rule needs one) / H-dead (apply step whose anchor no
longer matches: emits nothing).
Controls (--controls): planted ungated clamp block -> H-hidden-change; planted gated block -> gated; planted delay-slot fix ->
correctness; coverage: s6892 walker guard appears as gated (ROGUESQ_S6892), fixup_selfbranch appears as correctness.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
