# NEXT: who writes/zeroes the +8 halfword of LUT entries? (G1c phase 2)
HYPOTHESIS-ID: g1c-phase2-drawdist
Facts (s6091): LUTSCALE=4 leaves dd3 failing at finder call 58-59 with totcnt=0 (nonempty 41). Capacity is not binding; call ordinal invariant.
Hypotheses: H-zeroed some path clears +8 (use/pin count) on every node and never restores it at dd3; H-never-set entries are inserted with +8 = 0 when the DL volume is large; H-fixed-demand ~58 calls happen in one fixed sequence and consume all evictable entries regardless of table size.
Discriminator, one build: log first 8 nodes' +8 (and chain length) at finder calls 1, 30, 58 plus grep-enumerated store sites to +8 (sh with offset 0X8) in funcs_6.c ~0x8001E230-0x80022300 wrapped with a counter; compare dd1 forced-call positive control.
Run: copy scratch/agent/soak_queue/done/s6091_lutx4_dd3.sh (tag), perl -e 'alarm 580; exec @ARGV' zsh it.
