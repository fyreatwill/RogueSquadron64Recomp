# NEXT (s7495)
HYPOTHESIS-ID: m3-zbuffer-region-live-stores

Work unit: class ET, the residue of ES (s7494). Retail (tools/s7494_es_oracle.zsh) shows buildAndRegisterDefaultMaterial
(stores at 0x8001804c/0x8001805c) writing 210 words, stride 0x108, into 0x787830..0x78E374 at t=6.6 s, i.e. INSIDE the 640 Z-buffer
extent 0x76A000-0x800000 (640x480; 0x7D4400 for 640x340), right after its own (640,340) call. Questions:
H-et-same (the port makes the same stores at the same addresses in the same phase: both runtimes put a live object in the Z region;
benign if the Z-buffer is not used again in that phase, retail design) / H-et-port-moved (port stores go elsewhere or the port's heap
hands out a different block: layout divergence, find the allocator input that differs) / H-et-zlive (the region is a live Z target
AND a live object at once in both: a retail bug the RDP Z clear / RT64 writeback would stomp; check whether RT64 writeback covers it).
Discriminator, ONE port run (dd1, L4 title boot is enough, ~15 s): arm the s7480 store tracker / ROGUESQ_S7493_WBLIVE_WATCH=787830 and
an exec log of buildAndRegisterDefaultMaterial (a0,a1, and the base pointer it stores through) + rs_malloc returns covering 0x787830;
retail side: rerun tools/s7494_es_oracle.zsh 0x787830 0x78E380 12 and add --watch-pc 0x80001acc (rs_malloc) to name the allocation.
Positive control: the s7494 oracle rows reproduce (225 block writes) and the port watch must log the 0.74 s Z-clear writeback.
Outcomes: same PC/addresses/order in both -> H-et-same, close ET; port differs -> H-et-port-moved; a writeback covering the live
stores after 6.6 s -> H-et-zlive.
After ET: take the next ITERATION 3c rung with an engineering action (CURRENT-TRUTH Next steps 2-9 are owner-look).
