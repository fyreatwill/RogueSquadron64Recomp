# Next work unit

HYPOTHESIS-ID: H-alloc-window-sched-switch

s4713: runVideoFrameTick's mode record at s2 is an audio config (0x5622 Hz, voice counts 17/16/15/18/18/32), varies per scene, flag 0x8010D211=1 => re-allocs are the game-requested retail path (A). Open: name the WRITER of the record at s2 (add r18 to the print via a fixup patch of the funcs_0.c callsite, then arm a rdram write watch on it for the writer PC).
Hypotheses: (A) writer is retail game code (scene-load audio setup) -> window is retail behaviour; next ask why allocation in that window faults. (B) writer is a port stub -> name and ORIGIN-justify.
Discriminator: writer PC attribution for the record's bytes 4..6 in the port.
