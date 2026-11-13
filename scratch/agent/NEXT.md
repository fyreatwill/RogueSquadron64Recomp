# NEXT (s7278): G5c QOS_ALL replicate on L4 (owner's Gerrard V) under the s7277 CPU toggle
HYPOTHESIS-ID: g5c-qos-default
State: s7277 L12 within-run toggle: CPU load 60 -> 49.4 fps + 5 gaps >= 250 ms; QOS_ALL=1 59.5 fps, 0 gaps (control 3/3). Single run per arm.
Hypotheses: H-qos-general (QOS_ALL removes load freezes on any level); H-level (L4's heavier windows still freeze with QOS_ALL);
H-fluke (s7277 cpu15qos was a lucky run: replicate shows gaps).
Commands (one game at a time, check HID idle >= 120 s + screen unlocked):
  env LOAD=cpu TAG=l4cpu LEVEL=4 zsh tools/s7277_toggle_load_arm.zsh
  env LOAD=cpu TAG=l4cpuqos LEVEL=4 GXE=ROGUESQ_QOS_ALL=1 zsh tools/s7277_toggle_load_arm.zsh
  python3 tools/s7277_toggle_score.py l4cpu ; python3 tools/s7277_toggle_score.py l4cpuqos
Expected: H-qos-general -> l4cpu shows on-window gaps, l4cpuqos 0 and ~60 fps: write the owner the default question (OWNER-OPT-INS row s7277).
H-level -> name the stalled thread (sample the process during an on-window gap). Do not change the default without the owner.
