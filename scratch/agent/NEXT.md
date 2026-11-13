# NEXT (s7265): fold s7264_stack_edge — which part of the WIDEWIN auto stack eats the side ground, and does WW help 16:9 at all?
HYPOTHESIS-ID: widewin-169-tv
State: s7264 showed the auto stack (R=48 + merge 0.4 + E16) erases WIDEWIN's side-edge gain (21:9 stack L/R -0.7/+0.4 vs STACK=0 -4.4/-5.0).
Queued: scratch/agent/soak_queue/s7264_stack_edge.sh -> tools/s7263_widewin_edge_arms.zsh, results scratch/s7264q/edge_{s169,m219,c219}.txt,
capfps_*.txt (each must show >=10 frames/s, else rc=3 void: check frontmost / lock), [s7233] widewin_r line per arm in the soak log.
Outcomes (hard80% fog=0 -> fog=1, side thirds):
- Control c219 (21:9 STACK=0) must drop >=3 on a side. If not: void, check capture and split, re-queue.
- m219 (21:9 R=0, merge+E16 kept) drops >=3 -> H-R: the R=48 radius cut eats the gain. Next: try R>48 (e.g. 56/64) or R applied only
  beyond the visible side frustum; measure cost in the heavy window (tools/g1e_owner_quiet_arms.zsh as s7262) and the edge here.
- m219 flat -> H-merge: merge/E16 flattens the far side cells into fog-coloured slabs; next: lower MERGE / raise E on side cells only.
- s169 (16:9 STACK=0) drops >=3 -> H-gain16 (WW worth it at 16:9 once the stack keeps the gain); flat -> H-free16, tell the owner WIDEWIN is
  pointless at 16:9 and close the 16:9 half.
- Any crash_lines >0 -> backtrace first.
If the soak has not run (owner active), do not wait: ladder 3c next open owner-look item, or offline work (read apply_s7233_widewin_r.py
to predict which cells R=48 skips relative to the 21:9 side frustum).
