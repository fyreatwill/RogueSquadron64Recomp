# NEXT: log the real caller of requestMissionTransitionMode(arg 2) at the observed mission fail
Read docs/M6-S5747-FAIL-ARM-CENSUS.md. Hypotheses: (H1) bool 0x6D arm (count[0x28]>0), (H2) another arg-2 caller (grep callers of 0x800FB190), (H3) bool-7 arm after all (s5728 control was weak).
Discriminator: fixup-script entry log in requestMissionTransitionMode (arg, ra, gate, bool[7], bool[0x6D], count[0x28]) with a mark-everything control; one keyed hold >=400 s, two arms concurrently. Land the log as tools/apply_*.py.
HYPOTHESIS-ID: g1-nonhealth-fail
