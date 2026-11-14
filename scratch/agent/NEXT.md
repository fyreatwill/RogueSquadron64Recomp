# NEXT (s7305): G5e - owner toggle sheets for ROGUESQ_DD_FOG_ALT=1,3 at dd8 16:9 on L5 and L10 (3-level sheet bar; L1/L4 exist)
HYPOTHESIS-ID: g5e-far-fog
State (s7304): opt-in held 300 s L1/L5/L10, 0 crash, 60/s, and cheaper (L1 heaviest20 9.69 vs 12.57 ms same soak).
Unit: reuse tools/s7303_fog_ke_sweep.zsh's arm line (scratch/s7009/arm.zsh <lv> 8 ... "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=1
ROGUESQ_DD_FOG_ALT=1,3" 120 180, same-run xor8 toggle) for lv 5 and 10, then build sheets with the s7303 sheet tool
(docs/owner_sheet_s7305_l5k3_fog_tog.jpg, _l10k3_). Patch control: the s7302 0.3,0.8 haze-all band must show >5% removed texture.
Hypotheses / outcomes:
  - H-melts: far horizon melts, near detail kept (removed texture near <3%) -> G5e waits on the owner's look only.
  - H-level-dep: L5/L10 near terrain loses detail (>5% near) -> level-specific ke (like RLEVEL) needed.
  - H-no-far: L10 has no far band at dd8 (light level) -> report it, sheet shows no change, still fine.
Needs keys/window: run with idle >=180 s and unlocked screen, else queue as a soak (# SOAK_NEEDS_IDLE=180).
