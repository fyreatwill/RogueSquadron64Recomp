# NEXT: G1 — name the inline writer of objective counter 2 (0x80138064)
Evidence (s5789): counter 2 rises 0->3 in both arms with set/increase never entered.
Candidates (static scan): datItemSetObjectiveBooleanCount, applyDatObjectiveTriggerEffect (funcs_15.c), updateNpcEffectIntensity, executeActorType1Effect (funcs_41.c).
Work unit: one patch script tools/apply_s5790_*.py (fixup-mirrored like apply_s5787_objcount_log.py) logging, under ROGUESQ_LOG_HUDBIT, entry of those 4 funcs (args + counter-2 value before/after on return is hard; log at entry and compare to get-log order) PLUS the get-change-log already present. Positive control: get lines; and each logged entry must show at least one call. Queue fire/nofire arms in one iteration.
Outcomes: a candidate logged immediately before each 1->2->3 step = writer named (then read its condition: why friendly/loss objects count); none logged -> write via memcpy/script bulk copy, use store watch on rdram 0x138064.
HYPOTHESIS-ID: g1-mission-progression
