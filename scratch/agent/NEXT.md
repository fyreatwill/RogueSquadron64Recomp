# Next work unit: who stops submitting tasks in audio-gap seconds (s4264)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4263: the 0x8011A818/0x8011A7E8 sends are spTaskSchedulerThread / dpInterruptHandlerThread task-completion notifications; no flag/queue gate (full=0, recv==send). In gap seconds (t~19-25, both arms) almost no tasks (gfx or audio) are submitted/completed, while VI retrace sends continue.
Hypotheses: (B1) the guest game-logic/main thread is blocked on a recv that is only satisfied by a task completion (self-feeding stall that breaks after 1-2 s on a timer/retry); (B2) the scheduler thread's own input queue (0x8011A408/0x8011A420?) is empty - submitters upstream are blocked elsewhere (e.g. on a loader/DMA/PI queue); (B3) the producer threads are running but skipping submission by a guest policy (frame skip).
Discriminator: one instrument, one run: in osRecvMesg_recomp, per guest tid keep (mq, flag, entered_ts); on return clear. Each second print the list of threads currently blocked (tid, mq, blocked_ms) - emit also at each [s4259] GAP. Healthy-second table is the control (different blocked set). Add sends-per-tid-per-mq for all mqs (not only tid 0).
Outcome map: single thread chain blocked on a queue whose sender is itself blocked => B1/B2 and the queue names the culprit; all threads runnable/polling => B3.
Reuse scratch/agent/s4263_gate.sh (copy to s4264).
