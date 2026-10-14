# Advance M5-AUDIO-PLAN: pick the next open step

HYPOTHESIS-ID: m5-audio-next-step

VI-640 stall thread parked (s4801: 0/24 on same binary, sample call and binary ruled out).
Next unit: read docs/M5-AUDIO-PLAN.md, find the first step not marked qualified/closed (CURRENT-TRUTH lists 4-13 and A14 closed; check for steps after 13 and the MORT/task-contract boundary), write 2-4 hypotheses + the discriminating measurement in this file, then run it as a queued/one-build experiment. If none remain open, do an M3 idiom-class audit that commits a guard, or go BLOCKED with a specific question.
Passive: if any run shows `vi-fs stalled=1`, record load/display context (see CURRENT-TRUTH #1).
