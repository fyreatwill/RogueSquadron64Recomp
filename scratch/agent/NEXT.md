# Next work unit: name the writer of the private-DMEM arm's t≈28 s crash (s4251)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4250: ROGUESQ_AUDIO_PRIVATE_DMEM=1 un-starves audio (48-52 vs 7-19 tasks/s) but 2/3 arms crash at t=28.2 s (tasks 1530/1574) in different frames.
Hypotheses: (c1) faster audio consumes guest sample streams faster and hits the fillSampleStreamRange list-head==0 race (s4230) — crash frames in guest audio code; (c2) a gfx/RT64 race exposed because the gfx thread now contends differently (copyToRAM frame); (c3) a wall-time event at ~28 s (cutscene phase 3 end) unrelated to audio rate.
Discriminator (one build, one run): run 3 more B pairs plus a C arm = lock ON but audio throttled? Cheaper: run B with ROGUESQ_AUDIO_UCODE=0 (silent control, same private flag) and B with ROGUESQ_S4230 probes (tools/apply_s4230_*.py); crash at 28 s in the silent arm => c3/c2; crash only with real audio and list head 0 => c1. Positive control: arm A still shows starvation in the same run.
Also: if B stabilises, consider flipping the default and fold into M5 plan (docs/M5-AUDIO-PLAN.md step).
Commands: env TAG=_N zsh scratch/agent/s4250_ab.sh ; python3 tools/s4250_summarize.py scratch/agent/soak_results/s4250_ab*/arm*.log
