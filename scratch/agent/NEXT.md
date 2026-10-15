# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4914 result: flag A (0x8011A8C8) is cleared by postSwapRdpReset (0x8001C12C, called from viRetraceHandlerThread 0x80019B1C) at 0x8001C15C, only if A!=0 and 0x8001BF20(1) returns nonzero. Two-recv frames = clear skipped at the first retrace (A=1 at first gfx wake), landing one retrace later.
Hypotheses: H-slot-not-free (BF20(1) returns 0 at first retrace because a buffer slot is still busy), H-state-gate (BF20 returns 0 for another reason, e.g. count byte -0x7153 / a gate), H-ordering (clear runs but AFTER the ack send, i.e. send precedes postSwapRdpReset in some path).
ONE build, one run: mark postSwapRdpReset entry + 0x8001BF20 args/return (fixup: add rs64_s4913_mark-style call with value) + dump slot-state bytes (base 0x8012_8EAA: -0x7156+i for i<count, count at 0x8012_8EAD) at each retrace and each acquire; cover the 1->2 recv transition (ROGUESQ_S4913_SKIP) with table keyed per retrace. Positive control: A 1->0 transitions from the poll thread must coincide with BF20 returning nonzero.
Outcome: BF20 returns 0 with all slots busy => find who frees the slot (host RT64 present?) and compare with retail via oracle; BF20 nonzero but A stays => read 0x8001C160.. path; clear after send => ordering bug.
If stalled, resume the M5 audio plan.
