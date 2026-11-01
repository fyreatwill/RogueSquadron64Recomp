# NEXT: G1e — cut the interpreter proper (~200 ns/RDP cmd after s6713) so dense lvl5 dd4 FPS60 tasks reach 60/s
HYPOTHESIS-ID: g1e-rsp-segment

State (s6713): fast RSP DMA default-on in owner config; dense tasks ucode 9.32 ms @35k cmds, 51.6 tasks/s (same-run, from
11.83 ms / 46.3). First fold SOAK-RESULTS lines for s6713_fast_lvl1_dd1 / s6713_fast_lvl10_dd4 (fbd sane? 0 crash/stall?).
If either failed, that is the work unit (root-cause the fast path).

## Hypotheses (remaining ~200 ns/cmd)
- H-vops: RSP:: vector templates (VMADN/VMADH/SDV/VMADM/VMUDL) are out-of-line calls from factor5_ucode despite -O2.
  Check with `nm`/otool which RSP:: symbols are called from factor5_ucode; try always_inline on the hot templates in
  lib/.../rsp_vu_impl.hpp or -O3 on the ucode TUs. Needs two build dirs (build/ vs build_vops/) run concurrently, same
  recipe, compare slopes (cross-build but slope-per-command, scene-independent; repeat both arms twice).
- H-probes-ucode: rs64_dlw_jump + rs64_inline_probe_route + e9prov per dispatch (~4%): gate in fixup_factor5_ucode.py behind
  `if (!rs64_g1e_fast)` (regen ucode via the cmake custom command), same-run toggle covers it.
- H-tlv: thread_local g_dmem_cur access via _tlv_get_addr (~1%).
Commands: `zsh scratch/agent/s6713_toggle.zsh 5 4 <arm>` (lvl, dd, arm); `python3 tools/g1e_fast_ab.py scratch/agent/m6/g1_lvl5s6713_<arm>/run.log`;
profile with `sample <pid> 6` + tools/sample_gfx_split.py.
Outcomes: H-vops worth >=10% -> land it, requalify; <3% -> interpreter is at its floor, write the G1e dd4 ceiling and
move to the next ladder rung (G3d / G3).
