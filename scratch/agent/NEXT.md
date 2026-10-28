# NEXT: who calls the DL-chunk pool init at pc 0x80018094, and when relative to the cache emptying
HYPOTHESIS-ID: g1c-dd-phase2
Facts (s6561): heapWalker splices (pc 80007A44/AA0/AFC) are legitimate and preserve the chain. The only chain-dropping head store is pc 80018094 (pool relink loop at 80018044, stride 0x108, head=base), once per attempt at begin 6016-6067, nv=80564800 len 2909.
Hypotheses:
- H-R1: it is the game's own recovery/rebuild (e.g. called when begin finds the cache empty, or on scene/level (re)init) -> then the collapse precedes it and the real cause is demand>supply at px2.
- H-R2: it is a level-reload/transition path triggered by something else (death, mission restart, our pose-lock harness), and it fires BEFORE the crash, dropping outstanding chunks that live per-mode lists still point at -> the crash (SIGBUS in submitSceneNodeRender) is dangling pointers from this reinit.
- H-R3: reinit is called repeatedly and only logged once by the row cap.
Discriminator (ONE build, ONE run, s6553_run.sh 4 2 same env as hw7): at pc 80018094 head-store log ra (g_rs64_last caller / ctx r31 of the enclosing function), begin number, len(cache) before, sum of per-mode list lengths (0x801163C8 table + the 0x8011xxxx/0x8012A4B0 siblings read by heapWalker) before, and per begin 5990-6100 the free-list length + per-mode list lengths. H-R1: reinit begin > empty begin and ra is the begin path. H-R2: reinit begin < empty begin or per-mode lists nonempty at reinit and crash follows within a few begins. Positive control: a heapWalker splice must show per-mode list length dropping to 0 in the same table.
Also compute supply vs demand per begin (sum lenNV-lenOH at splices vs pops) to explain px2 depletion. Do NOT redo head-store classification or REACH.
