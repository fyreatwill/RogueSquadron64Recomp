# NEXT: owner reports first; otherwise the RSP-side DPC register model vs hardware
HYPOTHESIS-ID: rsp-dpc-reg-model
Context: the recompiled-RSP layer and its runtime are audited end to end (s7091 fixups, s7092 VU memory + divide,
s7093 scalar lowering, s7094 SP DMA + SP cop0: one off-by-one fixed in rsp.cpp audio ucode_data staging). What is
left on the RSP side is the DPC (RDP command) register model the ucode reads and writes: mfc0 DPC_STATUS /
DPC_CURRENT / DPC_END and mtc0 DPC_START / DPC_END / DPC_STATUS (gfx TU lines ~396-464 and ~2444-2515, audio TU 17/38).
RSPRecomp emits RSP_DPC_STATUS_READ() etc. (../N64Recomp/RSPRecomp/src/rsp_recomp.cpp; fixups in
tools/ucode_fixed/factor5_ucode_recompiled.c.patch); the bridge is src/rsp/dpc_bridge.cpp.
Hypotheses: H-dpc-ok (every value the ucode branches on matches what hardware returns at that point: XBUS/DMEM bit,
START_VALID, END_VALID, CMD_BUSY/PIPE_BUSY, CURRENT advance) vs H-dpc-shape (a status bit the ucode polls is returned
differently, so a wait loop exits early/never, or CURRENT is reported before the RDP consumed it, changing the
ucode's buffer-wrap decision) vs H-dpc-xbus (the ucode toggles XBUS via DPC_STATUS writes and the bridge ignores it).
Unit (offline first):
1. tools/s7095_dpc_census.py: list every DPC mfc0/mtc0 site in the 3 TUs, the bits each branch tests (andi masks),
   and what the bridge returns / does for each (code-read of dpc_bridge.cpp + RSPRecomp's lowering).
2. Reference: angrylion/parallel-rdp or cxd4 DPC handling + n64brew DPC_STATUS bit table; name each mismatch.
3. If a mismatch is live, one passive counter run like s7094 (ROGUESQ_S7094_DMASHAPE pattern, one gated call),
   L6 boot to flight `zsh scratch/s7094/run.zsh` with the env swapped.
Controls: site-count control (DPC site totals equal the census grep); positive = a mutated bit mask the detector flags.
