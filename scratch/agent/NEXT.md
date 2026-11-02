# NEXT: G1e — re-measure real game fps per draw distance on the current binary (s6775 follow-up)
HYPOTHESIS-ID: g1e-fps-remeasure

s6774 (aligned DMEM fast paths, -6.5%) and s6775 (constant DMEM base in the gfx ucode TU, -1.6..-3.4%) cut ucode ns/cmd ~10%
since s6716 measured FPS60 dd2 ~48-50, dd3 ~47, dd4 ~44 game fps. s6775's op-bucketed profile (tools/g1e_op_bucket.py) says no
DMEM accessor lever is left: remaining ucode self = VMAD*/VMUD* math ~35% (accumulator ACCL/ACCM/ACCH in memory), generated .c
body ~28% (MIPS GPRs in stack slots), SDV/SSV fast paths ~14%; rsp_dpc_submit_impl ~11% of ucode inclusive.
Hypotheses (one run per dd, same recipe, splits them):
- H-ucode: dd4 still < 60 and ucode_ms per task is the largest term -> next lever is the VU accumulator (keep ACC in locals
  across a straight-line run of VMAD*), measured with the same toggle discipline.
- H-bridge: rsp_dpc_submit_impl / RT64 submit dominate the per-task time at dd4 -> work the bridge copy path.
- H-done: dd2-dd4 now reach ~60 fps (tasks/s) in flight -> G1e is closed for the owner's settings; write the table into
  CURRENT-TRUTH and take the next ladder rung.
Work unit:
1. Fold soaks s6775_dmembase_lvl1_dd1 / s6775_dmembase_lvl10_dd4 (fail on "TLS FALLBACK HIT" or crashlines).
2. For dd in 1 2 3 4: `env HOLD_S=200 zsh scratch/agent/s6716_bridge.zsh 5 $dd fps$dd` (one at a time; FPS60, no logging).
   From each run.log phase 7 [g1e-split] rows: tasks/s (game fps), ucode_ms/task, submit/rest ms; [g1b] sd_wall.
3. Table dd x {fps, ucode ms, ns/cmd, calls/task}; compare with s6716. Pick the hypothesis by the dominant term at dd4.
Discriminating outcome: fps at dd4 and which per-task term dominates.
