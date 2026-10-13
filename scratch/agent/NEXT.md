# Consume queued gated-sampler soak, then resume strategic priority

HYPOTHESIS-ID: vi640-stall-vs-512

s4793: 0/3 froze (640 -> 1024 at 49-55 s). A 5-run version is queued at scratch/agent/soak_queue/s4793_gated_sample_x5.sh (output in soak_results/s4793, shares dir; check summary.txt for FROZEN + run*_stall.txt). If FROZEN appears: read the sample's Gfx/SP Task/main frames (cvwait => H-A, guest wait fn => H-B, Metal/SDL => H-C). If none, close the thread as non-recurring and pick M5 plan step (docs/M5-AUDIO-PLAN.md) next.
