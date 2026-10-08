# Next work unit: what blocks the guest audio producer at the stall? (s4246)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4245: steady-state audio tasks = AI set-next = 60/s; at t~18.5 (task ~1061) tasks stop while AI/VI continue (single run; run then died in Metal thread). See PORTING-STATE Session 4245.
Hypotheses: (a) the audio thread blocks on a message/semaphore the port delivers late or never (e.g. an RSP/DP done event, or a VI-synced message); (b) scheduler is busy/blocked on a graphics task (RDP fence) so audio tasks starve; (c) stall is artefact of the Metal-compiler fault (shader compile stall in the same run) and not audio-specific.
Discriminator: rerun scratch/agent/s4245_rates.sh twice, plus log at the stall the scheduler's pending-task queue depth and the thread each is blocked on (reuse [vi-wait]/[sp-task] logs near the stall; grep around the last task_enter increase). Outcomes: stall recurs at fixed time and graphics task also stalls => b/c; audio-only stall with VI+gfx tasks continuing => a.
Positive control: [s4245] window shows task_enter flat while setnext rises.
