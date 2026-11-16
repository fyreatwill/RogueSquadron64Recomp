# NEXT (s7438)
HYPOTHESIS-ID: rt64-gfx-terms

Class CU (CURRENT-TRUTH Next steps item 1): the remaining RT64 terms on the Gfx thread, in ONE table (iron rule 14).
s7434 named rs64LoadBlockRuns 0.32 (our lib/rt64 patch), decodeTriangles 0.28, processRDPLists 0.27 ms/frame; s7437 closed
TMEMHasher (0.49) as H-known.
Step 1 (offline, no build): tools/s7438_rt64_terms.py, reusing tools/s7437_tmem_hash.py's parse(): for the Gfx Thread (and
RT64 Workload/Present), charge each running self sample to its innermost RT64:: (or rs64*) frame, and also accumulate inclusive
per RT64 function; rank top 20 in ms/frame over scratch/s7435 (control column must pass, expect +0.0345) and scratch/s7433
--second-line. For each term >= 0.2 ms/f, grep PROJECT-OVERVIEW / PORTING-STATE for a prior closure (s6935-s6961 G1e LoadBlock /
TMEM work, s7018, s7028) BEFORE proposing any build -- s7437 showed the step-2 counter had already been run in s6942.
Hypotheses: H-closed (every term >= 0.2 ms/f has a measured prior closure -> close class CU, take ITERATION 3c next rung),
H-new (a term >= 0.3 ms/f with no prior lever -> name it, design one same-run toggle build), H-diffuse (no RT64 term >= 0.2).
