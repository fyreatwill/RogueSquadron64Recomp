# NEXT (s7867)
HYPOTHESIS-ID: g3-ai-dma-model
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7865): H-dma selected offline (tools/s7865_ai_dma_rate.py): mupen gap-free AI rate 1.916714 buf/VI (D = 768*551 =
423168 cycles, VI delay 811092), retail 1.914459 -> FIFO idle 0.118%. H-const refuted: no constant clock is retail.
Unit: implement ROGUESQ_AI_VI_CLOCK=3 in lib/N64ModernRuntime (events.cpp VI thread + ai.cpp osAiSetNextBuffer_recomp):
- at queue, stamp q_k = vi_count + host fraction of the current VI (steady_clock since last VI / VI period);
- model 2-entry FIFO: start s_k = max(q_k, e_{k-1}), e_k = s_k + 423168/811092 VI; post OS_EVENT_AI on the first VI tick
  >= e_k (mupen's AI_INT lands mid-VI; the guest sees it at its next wait - check that this rounding matches by the hist);
- log per buffer q,s,e at 3600-VI cadence like s7864. Then export.sh + commit, rebuild, rerun b17 det pair p1
  (tools/s7849_det_pair.sh as s7864 v17, PP_OVR/AP_OVR) with =3.
Outcomes: b17 H-exact past t1124 -> det sweep 18/19 exact, open b(other 2 forks) with =3; still forks at t1124 but residual
smaller -> queue-latency (q_k) resolution is the limit (H-unmodelable: close det sweep as timing class, s7863 stands);
histogram leaves {1,2} -> model bug, fix first. Budget: 1 more iteration on this slug after this one, then close.
Gate: any events.cpp/ai.cpp edit must keep s7538_gb_census (add the =3 site to the ai-vi-clock rule), s7363 (unsigned
clamp), s7383/s7633 green - run `python3 tools/s7651_gate_sweep.py` before committing.
