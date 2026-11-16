# NEXT (s7475)
HYPOTHESIS-ID: guest-heap-data-integrity

Class ED (in-block overrun inside the guest heap). EB proved the header chain is clean on all 19 levels at a 250 ms
cadence. What it does not cover: a write past a block's requested size that stays inside the slack before the next header,
or a header that gets restored within one check interval.
Design (one build, one instrument):
1. Read the rs_malloc / rs_free code (upstream_compat.cpp s7472_check names the arenas 0x8010FEFC/FF00/FF18) to get the
   request size vs the block size. On rs_malloc exit (host hook, env ROGUESQ_S7475_CANARY=1), fill the slack bytes
   [req, blocksize) with a 0xA5 pattern and record (blk, req, size) in a host table. On rs_free entry, and on every
   s7472 walk, check the slack. Report `[s7475] tail-hit blk= req= off= val= caller-ra=` with a budget of 40 rows per phase.
2. Positive control: ROGUESQ_S7475_CANARY_PLANT=<s> writes one byte into the slack of a live block in flight. It must be
   reported within one walk.
3. Run tools/s7472_heapchk_recipe.zsh-style LV lists (add the canary env to C=). Start with "4:4 7:4 12:4 15:8"
   HOLD=220, with the plant on the first arm.
Hypotheses: H-slack-clean (0 non-plant hits) / H-slack-hit (hits: name the caller RA, then add a write watch on that slack
word to get the writer PC, and fix the root cause with an ORIGIN line) / H-req-unknown (the request size cannot be
recovered at exit, so fall back to canaries only on blocks with size > req + 8).
