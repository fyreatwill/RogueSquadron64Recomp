# Next work unit: locate RT64 CPU hotspot in the send_dl stall (s4268)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4267 result: stall (t=21-26) is >=95% RT64 processDisplayLists CPU (fullSync body 300-500 ms non-wait + interpreter ~300 ms), waits ~0. Audio gap is host-renderer, not M5.
Next: ONE sample-based profile (macOS `sample <pid> 5 -file` during t=22-26 of scratch/agent/s4267_single.sh) as discriminator; top frames name the hotspot (texture decode / draw-call list growth / checkRDRAM / mutex). Control: sample at t=10-14 healthy for comparison. Then decide: fix in lib/rt64 (export.sh + commit) or park as host perf.
Then return to re-ranking M5 de-stub steps (docs/M5-AUDIO-PLAN.md); gap is not an audio defect.
