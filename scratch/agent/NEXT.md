# NEXT (s7494)
HYPOTHESIS-ID: m3-boot-fb-over-released-heap

Fold first: soak s7493_er_levels (L1 dd8 21:9, L7/L10/L12 dd4; tools/s7493_er_recipe.zsh). score=0 = every arm 0 age>=2/never
writebacks outside CTL, CTL caught, nobase=0 -> ER CLOSED 6 levels. score=4 -> read the `[s7493] wb ... age>=2|never` rows (exact base,
so a row is a real stale pair: fix in lib/rt64, export.sh + commit). score=3 -> control/contract failed, read which.

Work unit: class ES, the s7493 seed's ground truth. In the port (dd1), boot frees heap block 0x80787810 n=6C30
(freeManifestSegmentAssets <- runIdleFramesAndLoadSaveData) and 0.217 s later sets a 640x480 colour image at 0x76A000, which covers
0x76A000-0x800000. Is that the retail layout?
Hypotheses: H-retail-same (retail boot also loads manifest assets into [0x787810,0x78E440) and later uses 0x76A000.. as the 640 fb:
benign reuse by design; close ES) / H-port-layout (retail never puts heap data there, or its 640 fb lives elsewhere: our heap top or
fb placement differs from retail at dd1 -> find which port change moved it; e.g. heap extent vs osMemSize, G1c/G1d carve).
Discriminator (ONE oracle run, tools/oracle/README.md): retail ROM, --secs 20, --watch-write 0x787810:0x78E440 (CPU/DMA writers of the
block: retail PCs + times), plus --watch-pc 0x80035500 (osViSwapBuffer; the shutdown table prints the VI origins). Positive control in
the same run: a whole-RDRAM watch must fire (~1.6M hits / 8 s, README) or a known-hot address watch. Outcomes: retail writes asset
bytes into the block before the 640 VI origin 0x76A000(+) appears -> H-retail-same; no writes there and/or no 0x76A000 origin ->
H-port-layout (then compare the port's [fbw]/VI origin sequence and heap bounds at the same boot phase).
If the oracle cannot attach or reach that boot phase in 20 s: lengthen --secs; it reaches boot and attract per README.
After ES: the M3 heap-audit series has no open class. Take the next ITERATION 3c rung that has an engineering action (CURRENT-TRUTH Next
steps 2-9 are owner-look); do not write a backlog-exhausted block.
