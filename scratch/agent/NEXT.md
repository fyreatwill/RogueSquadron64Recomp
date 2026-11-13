# NEXT (s7263): fold s7262_169_widewin — does WIDEWIN (and its auto stack) matter on the owner's 16:9 TV recipe?
HYPOTHESIS-ID: widewin-169-tv
State: WIDEWIN heavy-window thread CLOSED s7262 (auto stack holds 60 at 21:9 dd4 on L1/L4/L5/L12, dd6 L4/L12; image clean L4 dd4/dd6,
L12 dd4 see s7262 entry). Owner plays 16:9 on the TV; every WIDEWIN number so far is 21:9.
Queued: scratch/agent/soak_queue/s7262_169_widewin.sh (results scratch/s7262q; L4 16:9 dd4 MELT; arms n=no WW, w=WW auto stack,
w0=WW STACK=0, w0d=w0+DUTY1.4 control).
Hypotheses / outcomes:
- H-free: at 16:9 the sides fit the retail 64x64 window -> w merged ~0 (or tiny), w ms ~= n ms. Then WIDEWIN is useless at 16:9:
  say so in OWNER-OPT-INS (TV: leave WIDEWIN off), close.
- H-cost: w0 ms > n ms by >1 ms and w merged >0, w ms < w0 -> the stack matters at 16:9 too; record 60/s holds, note in OWNER-OPT-INS.
- H-crash: any alive=0 -> backtrace (merge rewrite first suspect).
Control: w0d must show clearly more <55/s s than w0, else re-run.
If the soak did not run (owner active), do not wait: take a 16:9 side-edge image measure offline from an existing 16:9 dd4 capture if one
exists (grep PORTING-STATE "16:9" + "raw"), else ladder 3c next rung.
