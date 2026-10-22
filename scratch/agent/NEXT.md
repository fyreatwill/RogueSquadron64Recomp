# NEXT (s5902): tally s5901 in-sphere samples by class-1 objective vs RET
Context (s5901): bolts travel 33 u median and enter spheres; blanket H-range refuted. Missing: which in-sphere ids are the 21 class-1 objective NPCs, and why s5856 cin=0 for ids 1cc/f1 although s5901 ratio<=1 (competing: H-scope cin only set for last row/ w mismatch; H-id: rs5841_cand not the collider owner at the sphere call; H-real: those ids are non-objective).
Discriminator (one build, one run): append c1f and descriptor id (s5855 `did`) to the [s5901] line and also log rs5839_obj (collider owner) vs rs5841_cand; raise the 30000-line cap to 60000 or sample 1-in-2 cycles; offline: for in-sphere samples, count by did/c1f and compare with RET list (ids 52/66/c6/86).
Positive control: in-sphere count for ids 52/66 must be >0 and match RET.
Recipe: scratch/agent/s5897_life.sh (tag in g1_fireall call is s5897_life; use a new tag by editing a copy in place before launching, do not git checkout it).
Edit both tools/apply_s5835_sphere_probe.py and live N64Recomp/RecompiledFuncs/funcs_16.c; analyzer tools/s5901_nn.py.
HYPOTHESIS-ID: g1-mission-progression
