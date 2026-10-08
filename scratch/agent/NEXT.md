# Next work unit: why does the SP task completion take ~1 s in gap seconds (s4265)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4264: in gap seconds tid3 (spTaskSchedulerThread) is blocked on 0x8011A7E8 while tid0 sends only ~1 completion/s there (healthy: 30/s); tid2/tid5 starve behind tid3; tid0 keeps submitting to 0x8011A420.
Hypotheses: (C1) a single long SP task (audio ucode LLE loop) occupies the RSP ~1 s; (C2) the host SP-complete notification is delayed/coalesced (timer or retry), the task itself finished fast; (C3) the task is a gfx task whose RDP/DP-complete wait (0x8011A818 side) is the real holdup.
Discriminator: one build, one run: at the host SP-task start and SP-complete send (find where tid0 sends 0x8011A7E8), log per task (task type, ucode ptr, start_ts, done_ts), plus RSP-halt timestamp. Gap-second tasks vs healthy tasks as control. C1: done-start ~1 s with type=audio; C2: RSP halt early, notify late; C3: type=gfx and DP-complete late.
Reuse scratch/agent/s4264_gate.sh (copy to s4265).
