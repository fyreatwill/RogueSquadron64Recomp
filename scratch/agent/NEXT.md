# NEXT: confirm spike Y=FD57 is the VGE guard-band clamp (DMEM 0x60) and check pre-clamp inputs vs reference VU
HYPOTHESIS-ID: g3c-owner-visual-b
s6373 RESULT: writer is vreg 6 SDV at ucode L_1740 (`vmadh $v6,$v4,$v0; vge $v6,$v6,$v29[1q]`, $v29=DMEM 0x60). Y=FD57 pinned while X varies -> Y saturated by VGE lower bound.
Work unit: extend rs64_spike_sdv_note to also log DMEM 0x60..0x6F (v29 source) and, at first FD57, a snapshot of rsp.vpu.r[4], r[5], r[6], r[29] (add hook at the VGE line via fixup script in tools/fixup_*.py or log inside SDV via `this`). Outcomes: v29 lane1 == FD57 -> clamp confirmed; then compute pre-clamp Y from v4/v5/recip: huge due to w~0 -> retail identical (ask owner on CULL_SPIKE default-on); moderate value clamped wrongly -> VMADH/VGE emulation bug, replay in ares/parallel-rsp.
Recipe: env ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_LOG_SPIKE=1 ROGUESQ_SPIKE_DMEM=1" HOLD_S=300 LEVEL=2 TAG_SUFFIX=s6374 zsh scratch/agent/g1_level_coverage_common.zsh
