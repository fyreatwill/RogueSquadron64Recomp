# NEXT: why are replayed patches missing from the live tree?
HYPOTHESIS-ID: replay-patch-presence

Why: s6862 found 9 replayed apply scripts whose MARK is absent from ../N64Recomp/RecompiledFuncs (s2463, s4221-3, s4300, s4466, s4560, s4602, s4680), and that left the s4563 guard with no setter. The replay exits on failure, so absence should be impossible. 205 replayed scripts have no MARK, so a behaviour patch could be missing unseen.
Unit: offline only. Replay into a scratch copy of a fresh tree (never the live one) or read the last [s4648-replay] output in scratch/agent/loop.log; find what removes the blocks. Then build a presence check for the no-MARK scripts from each script's inserted text.
Hypotheses: H-skip (the live tree was built with RS64_SKIP_REPLAY=1 or a partial path) / H-strip (a later step such as the s6715 probe gating removes them on purpose) / H-order (a later patch rewrites the anchor text).
Discriminator: does a scratch replay contain the 9 MARKs? Yes -> H-skip. No -> find the first step after which each MARK vanishes (H-strip or H-order). Control: s4296 A14 yield MARK must be present in the same check.
Outcomes: any behaviour patch missing -> restore through the replay and A/B it. All probes -> extend tools/audit_heap_addr_tests.py into a post-regen check, remove the dead s4563 check, take the next ladder rung.
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
