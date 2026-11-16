# NEXT (s7480)
HYPOTHESIS-ID: canary-zero-slack-blocks

0. Fold scratch/agent/SOAK-RESULTS.md: s7479_canary_pad_a5 (PAD=16 FILL=0xA5, L4/L7/L12 dd4, L15 dd8 21:9, HOLD=220).
   Pass = boots with 0xA5 fill (confirms the s7476 ED fix removed the A5 boot hang), plant DETECTED, tail_hit_nonplant=0,
   slack_store=0, noslack=0 on every arm -> class EG closed for host writers too (record in CURRENT-TRUTH item 1).
   - Boot hang at A5 on any arm -> some code reads uninitialised heap slack/padding (a retail-invisible read of past-request bytes):
     rerun that level with ROGUESQ_S7475_BT=1 + ROGUESQ_S7475_SEL bisect (s7475 tool) to name the reader.
   - Non-plant tail-hit with no slack-store row -> a HOST writer (memcpy/PI DMA/RSP) overran a request: read its [s7478] alloc-bt
     chain, name the writer, fix the root cause.

1. If the fold passes, class EG is fully closed. Next M3 idiom class (ITERATION.md item 3; owner G5 items are all awaiting the owner's
   look per CURRENT-TRUTH headline): pick the next un-audited idiom from CURRENT-TRUTH Next steps (grep-enumerate, classify every
   site, guard or prove dead, close the class) and write a fresh NEXT.md with a NEW HYPOTHESIS-ID.
