# Next work unit

HYPOTHESIS-ID: H-alloc-window-sched-switch

s4712: all 6 port re-allocs come from runVideoFrameTick@0x8000153C -> reapplyDisplayMode (retail version has no skip). Open: why does the port take that branch 6x in 150 s when retail boot/attract takes it 0x in 120 s?
Hypotheses: (A) retail takes it identically once its scene reaches the same transitions (retail oracle only covers boot/attract, so 0 is uninformative past attract); (B) port-only: guard values (flag byte 0x8010D211 via lbu -0x2DEF($v0) @0x80001508, `4($s2)` @0x80001514, the byte tested at 0x800014F8) are set by a port-synthesised mode-record writer at 320->640 boot; (C) retail takes it too, but at attract widths we did not log.
Unit: one build adding, at the runVideoFrameTick guard (0x800014F8..0x80001518, fixup patch, env ROGUESQ_LOG_ALLOC_CALLERS), a print of the three guard values + s2 record bytes + width/origin on EVERY frame where the branch is taken, plus the same read in the retail oracle (tools/oracle/README.md: watch writes to 0x8010D211 phys 0x10D211 and exec at 0x8000153C, whole-RDRAM positive control first). Discriminator: retail hits in the first 120 s with same widths => A/C; none, and the port's record writer is a port stub => B (name the writer, ORIGIN rule).
Note: entry ra is 0 in callee hooks; use the static caller.
