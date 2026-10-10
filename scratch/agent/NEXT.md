# NEXT: who makes 0x801793F0 allocatable inside the live 120 KB block 0x801767E0?
HYPOTHESIS-ID: m5-audio-destub
Facts (s4556, 2 arms): rs_malloc 0x801767E0 size 122880 is never rs_free'd; later rs_malloc 0x801793F0 (664) and 0x80179480 (73728) land inside it, the latter covering audio node 0x80179510.
H-A: game/audio code carves the 120K block and rewrites its header/free list (legit retail behaviour). H-B: port-side free-list corruption. H-C: parent freed via a path that bypasses rs_free (inline header rewrite).
Discriminator: one run with a store watch on header 0x801767D0..0x801767E0 and on the free-list link pointing at 0x801793E0; print writer pc for the first store after the parent malloc. Also oracle-check retail's rs_malloc return for the 664-byte request. Control: whole-RDRAM watch fires.
Note: heap logging suppressed the crash repro; keep logs lean or use watches instead.
