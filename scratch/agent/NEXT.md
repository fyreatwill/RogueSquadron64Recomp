# NEXT (s7306): G5e - ROGUESQ_DD_FOG_ALT=1,3,1 at dd8 21:9 (owner's ultrawide): L1 toggle sheet + L1/L5 300 s hold
HYPOTHESIS-ID: g5e-far-fog
State (s7305): 16:9 qualified (s7304 hold, sheets L1/L4/L5/L10; L10 untouched by fog, lever ctl null). 21:9 never measured with the opt-in.
Unit: `zsh tools/s7303_fog_ke_sweep.zsh` is 16:9-only (ASP=16:9 CW=960 CH=540); copy it to tools/s7306_fog_219.zsh with ASP=21:9
CW=1120 CH=480 (check arm.zsh for the 21:9 vars used by s7298), run l1k3:1:1,3,1 and l1c:1:0.3,0.8 (lever control must remove >5%).
Then a 300 s hold L1/L5 21:9 with FOG_ALT=1,3,1 (reuse the s7304 soak recipe in soak_queue/done with ASPECT=21:9 MISSION_WIDTH=1024).
Hypotheses / outcomes:
  - H-same: 21:9 near removed <3%, far melts, hold 0 crash 60/s -> opt-in valid at both owner screens; OWNER-OPT-INS note.
  - H-side: the wide side band loses detail (>5% side) because the 21:9 frustum widening puts near cells at the fog end -> scale ke by aspect.
  - H-cost: 21:9 heaviest20 rises vs no-fog -> report; unlikely (16:9 was cheaper).
Needs keys/window: idle >=180 s and unlocked screen, else queue as a soak (# SOAK_NEEDS_IDLE=180).
