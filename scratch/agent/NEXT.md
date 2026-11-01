# NEXT: G1e — overlap the RSP LLE with RT64 RDP processing inside the gfx task
HYPOTHESIS-ID: g1e-gfx-overlap

s6704 established (two lines + same-run toggle with positive control): FPS60 = 60.0 fps at dd1, 44-50 at dd2-dd4, and the
binding term is the per-task gfx cost on the Gfx thread (send_dl), which runs RSP LLE emulation (~55% self) and RT64
processing of each DPC submit (submit_rdp_range -> processRDPLists, ~46% inclusive) SERIALLY; dp_complete only after both.
Game thread 5% busy. The no-op hook gate was refuted as the lever (<0.7 ms/task).

## Work unit
1. Read first: src/rsp/dpc_bridge.cpp (rsp_dpc_submit -> submit_rdp_range), src/main/rt64_render_context.cpp:1265
   (submit_rdp_range), events.cpp send_dl/dp_complete ordering (~l.1160-1205).
2. Hypotheses:
   H-overlap: RT64 work can run on a consumer thread while the RSP continues; send_dl wall falls toward max(RSP, RT64).
   H-dep: the RSP reuses the RDP output buffer (ring) within a task or RT64 must see RDRAM state as of submit time, so a
          naive async consumer reads overwritten commands (expect: garbage triangles/missing geometry in the toggle's on windows).
   H-rt64-bound: RT64 processing itself (TMEM hash, loadBlock, decodeTriangles) dominates once overlapped -> next lever is RT64.
3. Build ONE binary: ROGUESQ_RDP_ASYNC=1 queues (lo,hi) ranges (COPY the command words at submit time if the output buffer
   is a ring: check the ucode's DPC_START/END pattern in a [g1d-word]-style dump first) to one consumer thread; send_dl waits
   for the queue to drain before dp_complete. Make it flippable at the [g1b] boundary like ROGUESQ_RSP_HOOKS_TOGGLE (extend
   that toggle or add ROGUESQ_RDP_ASYNC_TOGGLE=10, tag hk/async in the [g1b] line).
4. Run lvl5 FPS60 dd2 300 s with the toggle; fold with `env HK=1 python3 tools/g1e_gfxbusy.py <dir> --tmin 140` (extend the
   split for the new tag). Positive control already exists: ROGUESQ_SPIKE_DMEM=1 under the toggle resolves +4.9 ms.
   Render check: fbd dumps in async windows vs sync windows, g1c terrain fraction + eyeball; any spike/garbage -> H-dep.
5. Success: async windows sd_ms down >=2 ms and tasks/s up, with identical frames. Then qualify 300 s lvl1/5/10 dd2 FPS60.
