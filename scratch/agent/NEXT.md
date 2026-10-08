# Next work unit: what is the game blocked on during an audio-submission gap (t≈22-30)? (s4259)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4258 showed dips are absent audio-task submissions, not slow host tasks.
Hypotheses: (A) audio thread blocked on a message queue the host never posts (e.g. AI/VI retrace or SP-done msg lost); (B) game main thread stalled in a spin (waitForAnyAudioSlot-like); (C) scheduler thread (spTaskSchedulerThread) asleep on its queue while tasks wait.
Discriminator: one build logging, during gaps >=0.5 s with no audio task, each thread's last guest PC / blocked-queue (osRecvMesg site) and the scheduler queue depth; 3 default arms via scratch/agent/s4257_ctrl.sh (arms 1-3). Queue depth>0 with no run -> C; depth 0 and audio thread blocked on recv -> A; main thread spinning -> B.
Also wire or drop the gfx_enter counter (always 0).
