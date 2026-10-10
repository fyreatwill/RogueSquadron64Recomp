# NEXT: score the thr11d post-exit stall from the s4546 intro-phase route, default vs HARD_SKIP

HYPOTHESIS-ID: wild-setcimg-writeback

s4547: the s659 freeroll recipe never engages in this build (6/6 pre-eng, no ALLOW_WILD_FL), so it cannot serve as the A/B. Use scratch/agent/s4546_wipe.sh / s4546b_skip.sh (these DO fire ALLOW_WILD_FL by default) extended past the intro, to see whether the fs stall appears with HARD_SKIP=1 vs default, interleaved, 3 each. Positive control: default arm shows ALLOW_WILD_FL in the same batch. If the stall is unreachable on this route too, decide HARD_SKIP policy with an ORIGIN line (writer of SETCIMG 0x130393 still unknown, s4531).
