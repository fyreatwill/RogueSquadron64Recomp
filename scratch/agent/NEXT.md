# Next work unit (s4297): consume the s4296 A14-yield soak, then resume the odd-control/512 route isolation

HYPOTHESIS-ID: m5-audio-destub-sequence

1. Read SOAK-RESULTS.md tail for s4296_a14_yield_title_hangar: expect 0 [a14-yield] rows, title 1024 ~14 s, hangar 512 ~26 s. Any [a14-yield] row = loop entered (new fact: record b0, a0/a1); a route regression = roll back with ROGUESQ_A14_YIELD=0 A/B.
2. Then the s4296-prior unit: isolate S4268 vs PHASE_WIDTH=1024 key gating (three concurrent RESTORE=0 arms: a+S4268; b without S4268; b with extended keys + PHASE_WIDTH=512) to find a route with odd>0 AND 512, then the hangar RESTORE A/B.
Next de-stub candidate if 1 is clean: the unbounded 0x8014974C spin (A12 note) with the same yield shape.
