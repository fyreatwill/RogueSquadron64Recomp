# NEXT (s7304): G5e - qualify the opt-in ROGUESQ_DD_FOG_ALT=1,3,1 (dd8 fog end 3) with a 300 s hold + frame ms
HYPOTHESIS-ID: g5e-far-fog
State (s7303): ke sweep monotone, ke3 melts the far horizon by eye, near detail kept (sheets docs/owner_sheet_s7303_*). Opt-in listed in OWNER-OPT-INS.
Unit: dd8 16:9 px8 auto recipe of s7294 (scratch/agent/soak_queue/done/s7294_169_dd8_levels.sh) + ROGUESQ_DD_FOG_ALT=1,3,1 on L1/L5/L10, 300 s each.
Hypotheses / outcomes:
  - H-hold-gain: 0 crash, 60/s, heaviest20 frame ms <= s7294 (shorter fog end also shrinks OFFMAPCULL K*fe) -> list as qualified, ask owner to judge.
  - H-hold-cost: frame ms rises or beyond-route seconds appear -> find which (the 1/dd^2 cutoff floor pulls the fog-blender switch in).
  - H-crash: any crash -> it is a side-effect datum, root-cause it.
Queue it as a soak (# SOAK_NEEDS_IDLE=600, it drives keys) and do offline work meanwhile; G5e can then close on the owner's look.
