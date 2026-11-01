# NEXT: G1e — DPC bridge per-command cost + in-ucode probes (dense lvl5 dd4 FPS60 at ~56 tasks/s after s6714)
HYPOTHESIS-ID: g1e-rsp-segment

State (s6714): ucode TU inlined (ROGUESQ_UCODE_INLINE_THRESHOLD=4000 default), slope ~185 ns/RDP cmd, dense tasks ~8.9 ms,
56 tasks/s. First fold SOAK-RESULTS lines s6714_inl_lvl1_dd1 / s6714_inl_lvl10_dd4 (0 crash/stall, fbd sane). A failure there
is the work unit (A/B with -DROGUESQ_UCODE_INLINE_THRESHOLD=0; suspect -O2 UB exposed by inlining, try -fwrapv).

## Hypotheses (sample B: factor5_ucode subtree interp 61% / bridge 31% / probes ~4%)
- H-bridge: per-DPC_END-bump path (rsp_dpc_submit_impl -> ultramodern::submit_rdp_range, rs64_dpc_record_submit, vector
  insert) costs ~55 ns/cmd; batching submits (only forward at full-command boundaries / every N kB, as RDP_STREAM does for
  the async worker) could cut most of it. Read src/rsp/dpc_bridge.cpp first.
- H-probes-ucode: rs64_dlw_jump + rs64_inline_probe_route + rs64_m4_* per dispatch (~4%): gate behind a cached flag in
  tools/fixup_factor5_ucode.py (survives regen), off in owner play.
- H-floor: interp is at its floor; remaining gap to 60 is scene-bound.
Instrument: ONE build carrying both changes, each with its own same-run toggle env (pattern: ROGUESQ_G1E_FAST_TOGGLE in
src/main/main.cpp ~4782); run `zsh scratch/agent/s6714_vops.zsh 5 4 <arm>` adapted with the toggles; fit with
tools/g1e_fast_ab.py (extend it to split on the new flag).
Outcomes: either lever >=5% of dense task ms -> land; both <3% -> write the G1e dd4 ceiling (dense ~56/s at dd4, 60 at dd1-2
with NODRAIN) into CURRENT-TRUTH and take the next ladder rung (G3 render fidelity).
