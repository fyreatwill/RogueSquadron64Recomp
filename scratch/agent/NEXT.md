# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4916: retail (oracle, control passed) = 60 swaps/s, one postSwapRdpReset per swap, slot bytes at its entry always (05, 00|01|02), never state 4. Port two-recv frames show (04,05) at that PC with BF20(1)==0.
Hypotheses: H-ordering (port's gfx thread commits state 4 in the middle of a VI-handler iteration, after the advance step but before postSwapRdpReset; guest threads are not strictly priority-scheduled), H-handler-late (handler's advance runs one retrace late for another reason), H-producer-early (gfx thread reaches mark-4 earlier than retail because the host RDP-done arrives early).
ONE build, one run: marks (rs64_s4913_mark, tids) at the handler's slot-advance stores (4->5, 5->0 in viRetraceHandlerThread 0x80019B1C..) and at bufferArbiterProducerMark's state-4 store; log tid + order per handler iteration. Positive control: marks fire at all in the same run and the advance marks precede psrr-entry in one-recv frames.
Outcome: mark-4 between advance and psrr-entry in two-recv frames => gate the host thread switch (handler non-preemptible by gfx thread until it blocks), then re-measure swaps/s; mark-4 never inside an iteration => advance is late, decode why.
If stalled, resume the M5 audio plan.
