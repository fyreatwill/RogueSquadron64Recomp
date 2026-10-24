# NEXT: G1c - read heap accounting, size the pool/heap
HYPOTHESIS-ID: g1c-draw-distance
Fold scratch/agent/soak_results/s6063_heap_px{1..4}_*.log: grep '\[heaplog\]'. Control: px4 must log a NULL malloc + top-8 live blocks.
Hypotheses: (A) live bytes at px2->px3 approach the heap ceiling, fit point exists (try px2.5); (B) a few huge live blocks (top-8 list) are a shrinkable consumer; (C) heap is fragmented (live << ceiling yet NULL) -> allocator issue, not budget.
Outcomes: peak near ceiling + big block identified -> shrink it or opt-in bigger heap; live far below ceiling at NULL -> fragmentation (C).
Then re-run tools/g1c_ddtog_fold.py with --hud on the best safe px for HUD/terrain.
