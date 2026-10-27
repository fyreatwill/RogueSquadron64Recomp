# NEXT: fold s6459 dd4 holds (G1c phase 2: how far can draw distance go)
HYPOTHESIS-ID: g1c-dd4-limits
Hypotheses: H-dd4-clean (farclip fix + cap scaling make dd4 hold like dd3), H-heap (guest heap exhausts at dd4, s6062), H-rsp-cost (RSP ms/s makes VI drop below 60).
Discriminator: fold SOAK-RESULTS s6459_dd4_lvl1/lvl5 logs: run.log 'multiplier 4', crashlines, vi_stalls30s, VI/s, RSP ms/s vs dd3 (~149 ms/s). Clean -> bundle dd4 option + owner sheet; heap/alloc failure -> carve second arena per CLAUDE/G1c phase 2 text.
Stale item 0 in CURRENT-TRUTH Next steps (dd3 missing mountain) was RESOLVED by s6418 farclip fix; ignore it.
