# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4919: retail hangar producer entry (0x8001BCE4) never parks (+6=2/3 >= +7-1=1 in 64/64, gated); port parks with +6=0 in 2,424/2,424. Open: what delays retail's producer re-entry by >=2 retraces after the 4->5 flip (0x800199DC).
Hypotheses: H-retail-gfx-slow (retail gfx thread blocked on RSP/RDP task completion; port HLE completes instantly so port producer arrives early and parks on retrace = natural pacing, likely benign), H-port-flip-early (port does the 4->5 flip too early relative to display), H-retrace-rate (retail 0x80019948 runs >60/s or double-counts).
ONE change: oracle count of 0x80019948 (retrace increment) and 0x800199DC (flip) and 0x8001BCE4 (producer entry), hangar-gated, 60 s, whole-RDRAM control; compute retraces between flip and next producer entry in retail and the event the gfx thread waits on. Compare with port bProd-entry/flip marks (s4918 log). Outcome: retail >=2 and port 0 with port gfx tasks completing instantly => park is benign pacing, close thread; retail ~0 on counter but +6 reads 2 => counter semantics differ, re-decode.
If stalled, resume the M5 audio plan.
