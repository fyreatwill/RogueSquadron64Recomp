# Next work unit (s4293): commit-bisect the title slowdown (frames to VI 1024)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4292: flags exonerated (4 arms x2). Exact s1950 recipe now takes #3120 frames to 1024 vs #786 at s1949 (d2663605). Frame rate unchanged => game needs more VIs => code regression.
Hypotheses: R1) a later M5/audio de-stub makes boot wait longer (audio-ready handshake); R2) a generated-code fixup added a stall; R3) lib/ patch change; R4) build/saves or environment changed.
Discriminator: git worktree at d2663605 (apply submodule-patches from that commit), build, run the s4292b 's50' arm; if ~#786 -> bisect between; if not -> environment (check build/saves first).
