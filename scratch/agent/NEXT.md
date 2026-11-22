# NEXT (s7789; s7788 closed the dead/partial emitter class: 0 dead replay steps, s563/s566 guards retired, census = s7719 step 5b)
HYPOTHESIS-ID: vendored-anchor-shadow-census
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Question: s7788 found vendored blocks that silently stopped matching because a LATER-in-file block (s2190 parity line, braced
stores) inserted lines between their anchor lines. The WARNING-emitting ones are now reviewed; which vendored blocks fail the SAME
way WITHOUT printing a WARNING (they `continue` / return quietly on count != 1, e.g. the `if marker in text: continue` idiom)?
Hypotheses: H-clean (every quiet-skip block's text is in the tree), H-quiet-dead (some block skips silently and its marker/code is
absent: list, say behaviour vs diagnostic), H-shadowed (absent, but another patch covers the same pc, as alloc-tail GUARD3/4).
Unit (offline): extend tools/s7788_dead_emitter_census.py with a per-block pass over fixup_game_funcs_vendored.py: for each
`text.count(<old>) == 1` / `.replace(<old>, <new>` site, derive a distinctive line of <new> and count it in the live tree
(controls: one known-live block e.g. s2190 scalar must read LIVE, the s563 block must read QUIET-DEAD). Review each absent
behaviour block (rule 11). Then `python3 tools/s7719_regen_gate.py --strict` (includes the census) and sweep --only 's778'.
