# Next work unit: confirm default private-DMEM removes the audio stall, then M5 Step 9/10 (s4257)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4256 made private audio DMEM the default (rollback ROGUESQ_AUDIO_PRIVATE_DMEM=0). Not yet measured in the default arm: audio tasks/s at t=18-28 s (s4250 saw 48-52 private vs 7-19 shared).
Use scratch/agent/soak_results/s4256_default/arm*.log (ROGUESQ_S4245=1 armed): count audio task_enter per 3 s window; expect >=45/s through t=28.
Positive control: one arm with ROGUESQ_AUDIO_PRIVATE_DMEM=0 should show the 7-19 dip. If the dip persists in the default arm, the flag is not taking effect (check the rebuilt binary). If it is gone, proceed to Step 10 (AI/SDL PCM join) or Step 9 per docs/M5-AUDIO-PLAN.md.
