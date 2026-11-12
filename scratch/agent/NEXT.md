# NEXT: AI stall recovery (s7197 follow-up)
HYPOTHESIS-ID: ai-stall-recovery
Context: s7197 (docs/HOST-COMPLETION-CENSUS.md) fixed the AI drain hazard. When the SDL device stops pulling, the drain
thread now posts AI every 100 ms (ROGUESQ_AI_STALL_POST_MS). While the device is stuck, the SDL queue grows by about 768 B
per post: remaining went 2597 -> 3365 -> 4133 ... A device that resumes, such as a TV switched back on, then plays that
backlog as latency, and nothing drains it.
Unit (one build, all arms):
 1. Extend ROGUESQ_AI_STALL_TEST in src/main/main.cpp get_frames_remaining to `<pause_s>:<resume_s>`, which unpauses at
    resume_s. Log queued bytes once per second ([s7198-q]).
 2. Arms, owner env, full logs, 60 s, pause 15 s, resume 35 s:
    - fix
    - fix + a backlog trim: SDL_ClearQueuedAudio when the queue has not shrunk for >= stall window, or when queued exceeds
      ~150 ms at the live rate
    - ctl
 3. Measure: queued bytes after resume, the audio-task ([s3299-t2]) rate after resume vs before the pause, and fallback
    count after resume (expected 0).
Hypotheses:
- H-recovers: the queue drains back to < thr within ~1 s of resume. There is no lasting latency, so close the thread.
- H-backlog: queued stays at the stuck-window size and audio lags video by that much. Land the trim (default on, =0 old).
- H-dead: audio does not resume. Then the SDL device state on resume needs a reopen.
Discriminator: queued bytes over time after resume, per arm.
