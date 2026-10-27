# NEXT: find what produces the constant Y=FD57 in $v6 (vmadh $v6,$v4,$v0 chain) - snapshot v0 and ACC
HYPOTHESIS-ID: g3c-owner-visual-b
s6374 RESULT: VGE clamp refuted (v29 lane1=F006 < FD57; value passes unchanged). v4 lane1=FFFD const, v5 lane1 varies, Y stays FD57.
Work unit: in the SDV hook also capture v0 and the 3 ACC lanes sets (ACCH/ACCM/ACCL) via vpu (add to sdv_lanes snapshot), and VCC/VCO; hand-replay vmudn/vmadh producing v6 lane1 against RSP semantics (ares vmadh: acc += (s32)vs*vt<<16). Outcomes: ACC/v0 explain FD57 exactly -> ucode math legit, FD57 is a real (retail) vertex Y: ask owner about CULL_SPIKE default-on; mismatch -> VMADH/VMUDN emulation bug, fix in rsp_vu_impl.hpp.
Recipe: env ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_LOG_SPIKE=1 ROGUESQ_SPIKE_DMEM=1" HOLD_S=120 LEVEL=2 TAG_SUFFIX=s6375 zsh scratch/agent/g1_level_coverage_common.zsh
