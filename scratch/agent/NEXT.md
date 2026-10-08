# Next work unit: which host-posted message arrives late during an audio gap? (s4260)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4259: during every t>=19 gap all 6 guest threads are blocked in osRecvMesg (thr0 main on 0x80149670, thr3 on 0x8011A818/0x80149990), d_recv<=1. Guest is idle, so a host-side message (VI retrace 0x80114388, audio/AI timer, SP/DP done) is late.
Hypotheses: (A) VI retrace posting stalls (gfx/RT64 frame long); (B) audio timer/AI message not posted; (C) SP-done for a gfx task late.
Discriminator: in the s4259 watcher, also log last-post wall time per target mq (hook enqueue_external_message + do_send by mq) and dump "ms since last post" per mq at each GAP; the mq whose age is >= gap and then resumes the main thread names the late source. Reuse scratch/agent/s4259_gap.sh (4 arms, GAP_MS=120). Positive control: CONTROL dump at t=20 must show ages for all active mqs.
