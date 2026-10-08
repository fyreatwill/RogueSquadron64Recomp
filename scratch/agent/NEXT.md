# Next work unit: who produces into 0x8010FEE0 / what does thr3 (0x8011A818) wait on during an audio gap? (s4261)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4260: VI and main thread run on time during t>=19.5 gaps; guest-internal queues 0x8010FEE0/0x80128D10/0x80149990 stale ~100 ms, 0x8011A818 stale 340-910 ms. No Timer/Ai/Sp/Dp host sources exist.
Hypotheses: (A) the audio producer is a guest thread gated on a guest-side condition the main thread no longer satisfies (e.g. an osSetTimer this port never posts); (B) a guest send into 0x8010FEE0 is dropped/refused (do_send full/guard refuse); (C) producer thread is blocked on a mq nobody sends to.
Discriminator: extend the s4260 table with last-sender guest thread id + do_send result (sent vs full/refused) per mq, and on GAP dump the sender thread's blocked_mq chain; also log osSetTimer/osSetTimerIntr calls (count, target mq). Reuse scratch/agent/s4259_gap.sh. Positive control: the CONTROL dump must list a sender tid for 0x80149670.
Also check whether the arm1-style 3.5 s total delivery stall (host posts enqueued, none delivered) recurs.
