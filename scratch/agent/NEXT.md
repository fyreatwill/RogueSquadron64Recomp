# NEXT: why do runs no longer reach the bad s4540 call (VI-640 bus error si_addr 0x380000000)

HYPOTHESIS-ID: odd-dma-alloc-pair

s4543: a no-print control (`scratch/agent/s4543_noprint.sh`) dies exactly like the print run (`scratch/agent/s4543_run.sh`). The print is innocent. 0/4 recent runs reach the bad call; s4540/s4541 did. Do not re-run the alloc-pair recipe unchanged (rule 8: 3 non-selecting iterations).

Competing hypotheses for the route change:
- H-flaky: the bus error is a nondeterministic race (thread timing); s4540/4541 were lucky. Discriminator: run the s4541-era recipe (ROGUESQ_LOG_S4539 unset, same env) 3 times concurrently in separate dirs; if ANY reaches the bad triple, flaky with rate p.
- H-patch: one of the apply_s4541/s4542 patches changed state. Discriminator: compare the first divergent line of run.log between s4541's saved run log and s4543's.
- H-env: an env var in the recipe (ROGUESQ_LOG_S4537/38) differs from the s4540 recipe. Check `git show` of the s4540 NEXT.md recipe.

Cheapest first: diff the env lists of the s4540 and s4541 recipes in PORTING-STATE against the current one, then run the 3-way concurrent batch (rule 13). Judge only by the bad triple. If the bad triple appears, read the count/base lines for count==32.
