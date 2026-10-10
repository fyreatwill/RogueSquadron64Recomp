# NEXT: what build difference since s4541 makes every run die at the intro VI-640 bus error

HYPOTHESIS-ID: odd-dma-alloc-pair

s4544: H-env and saves refuted; 3/3 more runs die in `fillSampleStreamRange+15156` ~3 s in (0/8 recent reach the bad call). Do not re-run the recipe.

Hypotheses:
- H-patch: a file in `git diff 0b7f286e..HEAD -- src build tools` (the s4542 apply script or the build itself) changed generated code that alters the route. Discriminator: `git diff --stat 0b7f286e HEAD`, then build the s4541 tree state in a SEPARATE copy (never git checkout over lib/), run the recipe once, check whether it reaches VI 1024.
- H-stale-binary: the current `build/RogueSquadron64Recomp` is not the s4541 binary plus the print. Check binary mtime vs `libRecompiledFuncs.a` and the committed apply scripts applied order.
- H-host: machine state (thermal/CPU load) changes thread timing. Weak; the crash is deterministic 3/3.

First: offline diff of s4541 run.log vs s4544_run1 run.log at the first divergent non-timestamp line (cheap, no run).
