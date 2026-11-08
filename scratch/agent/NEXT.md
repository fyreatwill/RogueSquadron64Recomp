# NEXT: G5b far-terrain drop measure on a second level (LEVEL=10)
HYPOTHESIS-ID: g5b-level-coverage
Context: G5i is fully verified (s6995/s6997/s6999) and closes on the owner's look; G5a/c/d/e await the owner. G5b's s6901
far-loss fix (EYEWIN=tog dose-response: quads p10 by heading, ring 5-7 dips, near<50) was measured only on LEVEL=4 (Gerrard V).
Read the s6901 entry (grep '^## Session 6901 ' PORTING-STATE.md) for the exact recipe and scorer (tog.py / fwd_smooth.py).
Hypotheses:
- H-general: the fix holds on LEVEL=10 at dd4 16:9 (armed quads p10 / ring dips like LEVEL=4).
- H-level: LEVEL=10's terrain layout/heading mix still loses far rings armed (dips persist) -> a level-specific cause remains.
- H-dd-only: drops on LEVEL=10 appear at dd4 but not dd2 (dose-response) even with the fix.
Discriminator, one binary, same-run =tog toggle (parity split is the positive control: site 15 must fire on the odd swaps):
LEVEL=10 needs ROGUESQ_FORCE_PLANET_UNLOCK=0xFF; check `cur`/[ddscene] level=10 actually flew (FORCE_UNLOCK clamps to level 1, s6991).
Arms: dd4 16:9, dd2 16:9. Report the s6901 table columns per arm plus a dd1 vs dd4 sheet.
