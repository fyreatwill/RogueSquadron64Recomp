# NEXT: locate the dd break point for missing ground (dd2/dd3 vs dd1), then name the dropping budget
HYPOTHESIS-ID: g1c-dd8-limit

s6468 showed dd4/6/8 flight frames lose the ground (see CURRENT-TRUTH top Next step).
Work unit: for existing dumps at dd2 and dd3 (g1_lvl1*dd2*, *dd3*) pick flight frames (fb 0x80620000/0x80690000,
stride 512), build one side-by-side sheet dd1|dd2|dd3|dd4 and eyeball ground presence; add a ground-presence
score (fraction of rows below horizon that are flat sky-blue) to tools/g1c_fbdump_join.py and validate it
against the dd1 (solid) and dd8 (missing) frames as the positive/negative control.
Outcomes: break at dd>=3 -> test pool/DL/vertex counters at that step; dd2 already broken -> s6074 "clean" is superseded;
no dumps available for dd2/dd3 -> one capture run of dd2 and dd3 lvl1 (position-pin recipe scratch/agent/s6468_dd8_sheet.sh).
