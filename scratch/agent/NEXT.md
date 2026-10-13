# Next work unit

HYPOTHESIS-ID: H-alloc-window-sched-switch

Voice +0x34 "late" is closed (s4708: name-string tail read via out-of-range voice index). Remaining question: in RETAIL, does the mixer run between the allocator's count store (0x8008F0CC) and base store (0x8008F0EC)?
Hypotheses: (A) retail never switches threads inside the window (our scheduler/ultramodern preempts where retail doesn't) -> fix is scheduling fidelity; (B) retail does switch, but count<=capacity there because retail never reaches a 6th alloc with a larger count -> upstream cause is the song-channel alloc sequence; (C) retail has the same race latently.
Discriminator: oracle (tools/oracle/README.md, physical addresses, whole-RDRAM positive control first) write-watch on phys 0x149700 and 0x1496F8 in retail through title->hangar; record count/base store order and whether mixer (0x800913xx) executions interleave. A 6th count store of 32 in retail selects (C)/(A); only counts 20,17,16,15,18 selects (B).
