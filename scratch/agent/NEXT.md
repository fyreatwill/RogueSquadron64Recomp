# Next work unit

HYPOTHESIS-ID: guest-2vi-wait

s4918: producer parks iff slot 5 present and byte +6 (retraces since 4->5 flip) < byte +7 - 1. Port hangar: +6=0 at producer entry in 2,424/2,424 parks, +7=02. Retail sample (48 rows) shows +6>=2 but was NOT hangar-gated (peek cap = first 48 hits, tools/apply_s4916_slot_peek.py:31).
Hypotheses: H-port-reenters-early (port gfx thread returns to producer <1 retrace after flip; retail >=2), H-retail-counter-differs (retail +6 is bumped elsewhere / reset not on 4->5), H-sample-artifact (retail hangar also shows +6=0).
ONE change: make the oracle slot-peek phase-gated (only count hits once --pc-phase-log phase armed, cap 2000), rerun s4918r_oracle_producer_peek.sh with a longer hangar window (more --press / secs 90; check phase-arm rows >0 as the control), tabulate +6 and +7 at 0x8001BCE4. Outcome: hangar +6>=1 => port gfx thread is too fast (look at what paces it: waitOnVideoQueue/task completion); +6=0 => retail also parks, contradiction with 60 swaps/s, re-decode.
If stalled, resume the M5 audio plan.
