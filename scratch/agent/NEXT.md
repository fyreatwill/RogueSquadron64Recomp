# NEXT: capture the VU op chain that leaves lane1 ACC=0xFFFF_FD57_FD57 (s6375 shows ACC consistent with v6 but not its producers)
HYPOTHESIS-ID: g3c-owner-visual-b
s6375 RESULT: v0=[0400 02A8 01FF 0], v4 lane1=FFFD, ACCH/M/L lane1=FFFF/FD57/FD57; v6 = ACCM clamp. Consistent, producers unseen.
Work unit: in RSP vector ops (rsp_vu_impl.hpp VMUDN/VMADN/VMADH/VMUDH/VMUDM/VMADM/VMUDL/VMADL) push (op,vd,vs,vt,e,ACCH/M/L lane1, vs lane1, vte lane1) into a 24-entry thread_local ring; dump the ring in the existing [spike-vr] block at an FD57 SDV. Hand-replay ops against ares semantics. Outcomes: replay reproduces FD57 -> ucode math legit, FD57 is real retail Y -> ask owner re CULL_SPIKE default-on; replay differs from logged ACC -> emulation bug in that op, fix in rsp_vu_impl.hpp.
Recipe: env ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_LOG_SPIKE=1 ROGUESQ_SPIKE_DMEM=1" HOLD_S=120 LEVEL=2 TAG_SUFFIX=s6376 zsh scratch/agent/g1_level_coverage_common.zsh
