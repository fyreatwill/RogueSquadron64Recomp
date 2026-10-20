# NEXT (s5655): split H-W2 (game stores) vs H-W1 (RSP DMA out) for the rail pattern in 1B2C60.. 
Facts: s5654 store census works (positive control OK) but only logs first store per PC with val=0.
Work unit (one build, one soak): (a) in rs64_s5654_vstore also log every store whose low16 of value is 0x8000/0x7FF8/0xF87F pattern (first 40) AND verify `value` is the stored datum (check one known sw site); (b) add a census of RSP DMEM->RDRAM writes (find the rsp_dmem_to_rdram path in lib/ or src/, grep it) that overlap 1B2C60..1B3600, log first 20 with task number. Recipe: copy scratch/agent/soak_queue/s5654_vstore_a.sh.
Outcomes: nonzero rail stores by game PC -> name PC/function, ask why (H-W2, then trace its source); RSP DMA writes into range -> H-W1, mix/ucode saturating (check ucode input gain/volume state); neither -> census blind (non-instrumented stores), widen.
Hypotheses: H-W1 DSP-produced saturated; H-W2 game-store/uninit fill; H-W3 refuted early.
HYPOTHESIS-ID: g2-voice-never-requested
