# UNBLOCK (s4648) — route 1 (refute) succeeded; block option 1 needed no authorization

Claim: "repairing the full-regen path needs owner authorization (N64Recomp scratch output, diff vs s4204-fresh)".

Refutation: fixup_game_funcs.py has ONE hard-coded output path (line 27, `base = ...`). A scratch copy with that
line repointed, run against a copy of the pristine `RecompiledFuncs.s4204-fresh`, never touches the live tree.
Observation: `scratch/s4648/scratch_s4648_scratch_fixup.py` ran it: rc=1 after "s2190 ... patched 51 files", aborting at
`s4339 C88C descriptor anchor count=0`. This reproduces the s4204-era abort safely; no human decision, no network, no live files.

Root cause of the abort (new): the anchor is the text of the s4332 probe, which exists ONLY in the live hand-patched
tree (funcs_27.c:2429) and has no patch in fixup_game_funcs.py. Same for many other tags: 168 of 384 distinct
`PATCH: sNNNN` tags in live RecompiledFuncs are absent from the fixup source (crude substring match, includes some false
positives; raw census in scratch/s4648/scratch_s4648_live_tags.txt). At least some are BEHAVIORAL, not diagnostic:
s4563 stale head (env-gated, default ON), s4296 A14 spin yield, s4580 holdmix, s4571c, s4572.
So a full regen today would silently change runtime behavior even if the anchors were fixed.

Route taken: 1 -> 3 (re-scope). NEXT.md holds the bounded work unit: classify live-only patches, backport behavioral ones.
Experiment that would refute this conclusion: after backporting, scratch-fixup output must `diff -r` clean against live RecompiledFuncs.
