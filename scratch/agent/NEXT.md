# NEXT: decide why selection 10/15 enters runModelViewerLoop (menu overlay) instead of initMission

HYPOTHESIS-ID: g1-mission-coverage-sweep

H1 levels 10/15 are legitimately viewer-backed (non-flight) entries -> mark as N/A for flight coverage, find what exits viewer.
H2 menuOverlayInit state after forced select is wrong (our force path skips a menu step) -> fix force route.
H3 recomp bug in 0x800C6900/0x800C9BF0 dispatch.
Discriminator: read funcs_34.c near line 7250 (RecompiledFuncs) for the branch using 0x800C6900(*s3); log its return for sel 10, 11, 15 in one run
(three recipes, same build); also fold 16b..18b soak results from SOAK-RESULTS.md.
