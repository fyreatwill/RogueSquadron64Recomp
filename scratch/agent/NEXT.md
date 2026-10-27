# NEXT: qualify dd4 on lvl10, then probe beyond 4x (G1c phase 2)
HYPOTHESIS-ID: g1c-dd4-limits
Hypotheses: H-dd4-lvl10 (lvl10 holds like lvl1/5), H-clamp6 (dd5/6 hits next limit: heap, ucode cap, pop-in, or VI<60), H-no-limit.
Steps: (1) queue soak scratch/agent/soak_queue/s6461_dd4_lvl10.sh modelled on done/s6459_dd4_lvl1*.sh with LEVEL=10. (2) edit tools/apply_s6036_dd.py:7 so clamp is 6.0 when ROGUESQ_DD_UNSAFE set (keep 4.0 otherwise), run regen order (make_elf -> N64Recomp -> fixup -> cmake), queue dd6 lvl1/lvl5 holds. Discriminator: run.log 'multiplier 6', crashlines, vi_stalls30s, VI mean, sd_wall vs dd4 (53-60 ms/s), alloc-failure lines.
