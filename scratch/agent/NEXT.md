# NEXT: G1e — split the dd4 gfx task's RSP segment (13-18 ms in dense scenes) into interpreter vs bridge vs logging, cut the winner
HYPOTHESIS-ID: g1e-rsp-segment

s6711 (tools/g1e_tl.py, ROGUESQ_G1E_TL): at lvl5 FPS60 dd4 (ASYNC=1 NODRAIN=1) a frame makes its VI iff the gfx task
(Gfx-thread start -> RSP ucode exit) < ~14 ms. Dense phase: 13.2 ms/task, 789 kB RDP out, 1626 defer calls; fast 4.6 ms.
Linear in output at ~17 us/kB. Guest run, VI phase and handoff latency are ruled out.

## Hypotheses (what is inside the 13-18 ms)
- H-interp: the LLE RSP interpreter itself (vector ops / dispatch) dominates -> cut via hot-path work in rsp_vu / ucode recomp.
- H-bridge: our in-RSP RDP bridge per command (src/rsp/dpc_bridge.cpp: spike cull default ON, defer-range bookkeeping,
  ~1600 rdpq submit calls/task) dominates -> batch/merge ranges, cheapen the cull.
- H-log: recipe-armed diagnostics (ROGUESQ_LOG_RDP_TRICOUNT, FB_HASH, LOG_RT64_DRAWN from m6_god_common.sh) cost per
  triangle -> owner play (no logging) is already fine; fix the recipe, not the game.

## Work unit (ONE build, ONE run)
1. Inside rs64_run_lle_gfx (src/main/main.cpp:7069) accumulate per task: total, time inside DPC/XBUS bridge callbacks
   (dpc_bridge entry points: wrap with a thread-local ns accumulator), time inside rdpq submit, and the RSP instruction
   count if cheap. Print per second with [g1e-aq] (G1B only).
2. Same-run toggle (window flip every 10 s at the [g1b] boundary, like ROGUESQ_RDP_ASYNC_TOGGLE): logging recipe vars
   OFF vs ON via a runtime gate (TRICOUNT/FB_HASH/DRAWN are env-static: add a toggle global), and CULL_SPIKE on/off.
3. Run scratch/agent/s6711_tl.zsh-style recipe (lvl5 FPS60 dd4 ASYNC NODRAIN, ROGUESQ_G1E_TL kept for the frame view).
   Positive control: interp + bridge + submit + rest == lleRun total per task.
Outcomes: bridge share >50% -> H-bridge; logging arm cuts >20% -> H-log; else H-interp.
Also fold the queued soak s6711_nodrain_hangar_route (hangar/menu render under ASYNC+NODRAIN) when it lands.
