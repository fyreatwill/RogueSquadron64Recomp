# NEXT: G1 — do class-1 NPCs in lv0 time out too fast, or does the port just never kill them?
(s5815 was a maintenance pass: CURRENT-TRUTH compacted 457->164 lines; no experiment run. Work unit carried over unchanged from s5814.)
s5814: msg2 = slot lifetime countdown (slotDispatcherIter byte +0x1A, flag +0x14&8) -> destroyNpcSlotByIndex; msg5 = handler-chain kill (8).
Hypotheses: (a) idle autopilot never kills, timeout is correct; (b) countdown is decremented too often in the port (extra dispatch passes per frame vs retail), NPCs expire early even for a real player; (c) countdown init wrong.
Discriminator (one build, one run): log per-slot +0x1A initial value at spawn and number of slotDispatcherIter passes per VI frame (positive control: passes/VI constant and nonzero), plus time-to-expiry in VI frames for each msg-2 NPC. Compare with retail via oracle if feasible (expected expiry in frames = init * passes-per-frame).
Command: scratch/agent/g1_inv1.sh <tag> 400  (instrument goes into a tools/apply_s58xx_*.py fixup script, not hand-edited generated code).
Outcomes: passes/VI ~1 and expiry ~ init frames -> (a), then drive aimed fire; passes/VI >1 -> (b), fix the pass rate; init differs from DAT value -> (c).
HYPOTHESIS-ID: g1-mission-progression
