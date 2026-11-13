# NEXT (s7272): G5c frozen-image check on the new WIDEWIN auto-stack path (owner 16:9 TV recipe)
HYPOTHESIS-ID: g5c-freeze-widewin-stack
State: widewin-stack-cutscenes CLOSED s7271 (H-clean at 21:9 and 16:9). The auto stack (R=88 + merge 0.4 + E16, s7233-s7266) is new code
since G5c (s6902) was checked; its merge pass rebuilds cells per frame and nobody has looked for multi-frame frozen images on that path.
Unit: one flight run, L4 dd4 16:9 FPS60 WIDEWIN=1 (auto stack) vs WIDEWIN STACK=0 in the SAME run via the existing tog3/tog clocks
(ROGUESQ_DD_WIDEWIN_R_TOG=3 _R3=0,88,88 _MERGE_TOG=3 _MERGE3=0,1,0, i.e. ph0 off / ph1 stack / ph2 R only), route = tools/s7263_widewin_edge_arms.zsh
(frontmost keeper, capture >=52 fps or VOID), capture 300 s of flight with scratch/s6914/g5b_capture, then tools/g5c_frozen_runs.py RAW 250.
Positive control (rule 1): the s6902 meter arm (PORTING-STATE grep 'g5c_frozen_runs', vc arm) or a deliberate ROGUESQ stall injection in
one phase must show a frozen run >=250 ms in the same raw; without it a zero is not a result.
Hypotheses: H-none (0 frozen runs >=250 ms outside loads in all phases) -> close; H-merge (runs cluster in ph1/merge phase) -> profile merge;
H-general (runs in all phases equally) -> host/present cause, G5c reopen with [s7064] timing.
If the host is busy or locked, queue it as a soak (SOAK_NEEDS_IDLE=120) and do offline work.
