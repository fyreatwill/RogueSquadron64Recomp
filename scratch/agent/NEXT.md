# NEXT (s7264): fold s7263_169_edge — does WIDEWIN show more side ground at 16:9?
HYPOTHESIS-ID: widewin-169-tv
State: s7263 folded the cost check: at 16:9 L4 dd4 WIDEWIN + auto stack = no-WW cost (9.15 vs 9.23 ms), WW STACK=0 +3 ms.
Queued: scratch/agent/soak_queue/s7263_169_edge.sh -> tools/s7263_widewin_edge_arms.zsh, results scratch/s7263q/edge_{a169,a219}.txt
(g5e_edge_score per toggle parity fog=0 off / fog=1 on, per third; hard80% is the metric).
Outcomes:
- Control: a219 left or right third hard80 must drop on fog=1 by >=3 points (s7009 right 16.1 -> 8.3). If not, the instrument is void: check
  [s7010-clk] split=parity in the run log and that frames are in flight (cols > 0), fix, re-queue.
- H-gain16: a169 side thirds drop >=3 points on fog=1 -> WIDEWIN helps the TV too: tell the owner in OWNER-OPT-INS (TV: WIDEWIN worth adding).
- H-free16: a169 side thirds within +-2 -> at 16:9 the 64 window already covers the sides; extra cells are hidden/fogged: OWNER-OPT-INS
  "TV: WIDEWIN changes nothing visible, leave it off", close the thread.
- Any crash_lines >0 -> backtrace first.
If the soak has not run (owner active), do not wait: ladder 3c next open owner-look item, or offline work.
