# NEXT: fold s5756_nogoda/b soak results — which setHudEnableBit4 caller ends an unpiloted mission
Task: read SOAK-RESULTS.md for s5756_nogod{a,b}; grep their logs for [hudbit]/[mtmst]/[objbool] lines before the results screen. Control: >=1 [mtmst] line, godrefills=0. Map the ra of the first setHudEnableBit4 to a function in N64Recomp/RecompiledFuncs (funcs_43/47/48 candidates, docs/M6-S5747-FAIL-ARM-CENSUS.md).
Hypotheses: H1 bool-0x6D arm (count[0x28]>0); H2 bool-7 arm via dialogue; H3 death path requestMissionTransitionMode(1) (lives--), not via setHudEnableBit4 at all.
Discriminator: ra of first hudbit hit + whether lives counter changes.
HYPOTHESIS-ID: g1-nonhealth-fail
