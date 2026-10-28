# NEXT: after the flight-scene pool reinit, why does px2 demand outrun supply (px1 does not)?
HYPOTHESIS-ID: g1c-dd-phase2
Facts (s6562): reinit at pc 80018094 is the game's flight-scene init (512x448 flight view, 2909-chunk pool); present in px1 and px2. px2 cache hits 0 in 14/14 runs 70-130 begins later; px1 never empties (len 661->1326).
Hypotheses:
- H-D1: px2 submits more DL chunks per frame (bigger terrain/dd4 footprint) than the pool supplies; chunks return via heapWalker only at a fixed rate -> linear depletion; the fix is a bigger pool (pool size is set by px, so check what px2 actually allocates vs reinit's 2909).
- H-D2: the reinit builds only 2909 chunks regardless of px (the px-scaled pool is a different structure), so px2 starves where px1's smaller demand fits.
- H-D3: heapWalker return rate drops at px2 (frame time) so supply falls behind.
Discriminator (one run each, px1 and px2, hw7 recipe, ROGUESQ_HEADWATCH=1 FROM=5900): per begin 6053-6140 log pops, heapWalker returned count (sum lenNV-lenOH at splices), and len. H-D1: pops/begin px2 >> px1 with equal return rate. H-D2: reinit len identical (2909) in both arms. H-D3: returns/begin lower at px2. Positive control: splices already log nonzero.
