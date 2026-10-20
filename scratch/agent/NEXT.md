# NEXT (s5689): fold s5688_bool7_{a,b} soaks (G1, Next steps #2)
Read scratch/agent/SOAK-RESULTS.md tail, then grep -a '\[objbools\]\|\[objbool\]\|\[ccosnap\]' on scratch/agent/soak_results/s5688_bool7_*.log.
H2: [objbools] list contains 7 or 1 (or ccosnap shows 7=1 with a preceding [objbools]) -> name the list pointer / static call site and what triggers it.
H1: only [objbool] id=7 from sayWhoaHim. H3: ccosnap shows 7 flip with NO [objbool]/[objbools] -> a third (direct store) writer; add a store watch.
Controls: [objbool] id=0x20 call#1 and ccosnap #1 must be present, else the run is void.
HYPOTHESIS-ID: g1-bool7-voice-path
