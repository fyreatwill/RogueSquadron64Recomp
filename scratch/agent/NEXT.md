# NEXT: L9 21:9 frozen poses for the s7061 level cap 8192 -> fold CAPLEVEL 9:8192 into the 21:9 auto bundle if invisible
HYPOTHESIS-ID: dd6-219-levelK-survey
Context s7061: cap 8192 holds L9's dense burst at ~60 fps (2 runs: 59.8/58.3/59.5 and 60.0/58.2/60.0 in 8192/10240/8192 phases). New opt-in knob
ROGUESQ_DD_WIDEWIN_CAPLEVEL=<lvl>:<cells> (src/main/upstream_compat.cpp rs64_s7012_cap), not auto. Image cost of 8192 on L9 is unmeasured.
Run (screen unlocked: /usr/sbin/ioreg -n Root -d1 | grep -c '"CGSSessionScreenIsLocked"=Yes' must print 0):
  zsh scratch/s7061/run_pose.zsh 9      (arms c10240 base / c8192 via CAPLEVEL / c6144 positive control; out scratch/s7062/L9)
Score: python3 tools/s7032_pose_cull_score.py --base c10240 <dir> (see s7052/s7057 usage in PORTING-STATE), plus eye the frames.
  Positive control: c6144 must show a difference > c8192 (if c6144 is ~0 too, poses are not on the wide edge -> move FZ later/earlier).
Hypotheses:
 H-invisible: c8192 <=0.1 mean |dLum| / ~0% px while c6144 shows -> add `9:8192` to an auto ROGUESQ_DD_WIDEWIN_CAPLEVEL in src/main/main.cpp s7037 block
   (next to the KLEVEL auto, FB_WIDTH>796, setenv overwrite=0, only if no explicit _CAP), log in [s7037], one 21:9 L9 auto hold to confirm [s7061] fires.
 H-visible: c8192 shows a band (like L4 c9216 in s7052) -> try 9216 the same way (poses + burst); if that also shows, record trade, leave opt-in, close L9.
Any crash: side-effect failure (G4 rule) -> capture and root-cause first.
