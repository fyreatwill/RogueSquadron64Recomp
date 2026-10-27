# NEXT: why do ~20% of dd4 cells still reject at SPANSCALE=16 (rec window vs span)?
HYPOTHESIS-ID: g1c-span-reject-predicate

s6524: dd4 EMPTY keys>=745: s1 28.3 / s4 24.3 / s8 19.9 / s16 21.1%, dd1 0% -> plateau; H-scale refuted as dominant.
Hypotheses: H-rec-window (far cells' rec[3]/rec[4] height window excludes the rasterized span: scale/offset rec by dd), H-span-offset (span bytes biased by dd-dependent origin, e.g. cell/win mapping), H-reject-by-design (far cells legitimately outside window).
Discriminator (offline, no build): from scratch/agent/m6/g1_lvl1s6524b_dd4s16/run.log, join [span-pred]/[cell-rec] rows of EMPTY returns; tabulate A,B,rec3,rec4 per rejected cell vs same cells at dd1 (dd1 never rejects). If A,B sit inside a consistent offset of rec window -> H-rec-window/H-span-offset (patch); if A,B are far outside (>100) -> by design.
