# Next work unit: snapshot RT64's list bytes at walk start for the garbage-cimg range (s4281)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4280: the 0x130393 w1033 SetColorImage is triangle coefficient data (bump==commit, range 4E28F8..4E2A58 = two intact CF triangles). RT64's walk (s4271DumpRing) saw CF at 4E27B0/4E2860 and E9 at 4E2910, but RDRAM at bump and post-commit has FF2E0C68 at 4E2910 and CF at 4E28F8/4E29A8.
Hypotheses: A) RDRAM changes between bump-time and RT64's read, then again before post-commit (concurrent writer / ring lap / next task); B) RT64's pointer/stride view differs (dl offsets against a different base, merged-list pend/continuation path); C) RT64 mutates dl words during the walk (E9 authoritative-fetch machinery).
Discriminator (one build, 6-9 runs of scratch/agent/s4280_walk.sh, hit rate ~2/9): in processRDPLists entry (rt64_interpreter.cpp) copy the list bytes [liststart, listend) (cap 0x40000) into a buffer; at the 0x130393 event (hook already in rt64_rdp.cpp) print words 4E27B0..4E2A58 from (a) entry snapshot, (b) live RDRAM at event time, next to the bridge shadow/commit already printed. Outcomes: snapshot==shadow but ring differs -> C or B; snapshot != shadow -> A (then word-store watch on that window to name the writer); snapshot==ring -> bridge shadow is the wrong range. Positive control: SANE cimg range snapshot==shadow.
Do not redo the bump/commit filter audit (R1 closed); do not chase audio-heap witnesses.
