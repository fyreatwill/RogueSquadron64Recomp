# Next work unit: split gfx starvation from audio-thread block at the t~18.5 stall (s4247)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4246: stall recurs at ~t=18.5 s in 2/2 runs without a Metal crash; task_enter drops from 60/s to ~0-30/s until t~25, setnext/VI continue; a pak-combiner/flush log burst precedes it.
Hypotheses: (a) audio thread blocked in osRecvMesg on a message delivered late (log mq + site); (b) scheduler serialised behind long graphics tasks (gfx enter/ok counts per second, task duration); (c) host-side RSP/RDP task completion slow (time per gfx task in run_task).
Discriminator: extend `rs64_s4245_tick` / rsp.cpp run_task hooks with per-second gfx (M_GFXTASK) enter/ok counts + max task wall time, and the audio thread's pending osRecvMesg site. Outcomes: gfx tasks long/continuous while audio tasks absent => (b)/(c); gfx idle and audio stalled => (a).
Positive control: queue==setnext and gfx enter==ok in pre-stall windows. Run scratch/agent/s4245_rates.sh twice (one at a time).
