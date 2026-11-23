# NEXT (s7865)
HYPOTHESIS-ID: g3-ai-dma-model
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7864): ROGUESQ_AI_VI_CLOCK=1/2 (+_BPV/_SEED) landed; port AI histogram {1,2} like retail (S7864_AIHIST), but bonus 17
still forks at t1124 in 3 arms (scratch/s7864/v17, v17b, v17c). The oracle's AI rate wanders (1.914588 to t1123, 1.914722 whole):
mupen (../rs64-oracle/iter974-armB3/src/device/rcp/ai/ai_controller.c) fires AI_INT LEN*floor(cps/(4*fs)) cycles after a DMA
STARTS, and starts it only once queued, so empty-FIFO gaps add guest queue latency.
Unit, OFFLINE first (no game run): from scratch/s7861/v17/r1/oracle.log (AI queue rows 0x8008EE08/EE84 carry VI; check whether
they carry cycle counts) compute the nominal per-buffer duration in VI units (vi delay = (v_sync+1)*count_per_scanline; read
vi_controller.c) and the gap structure: per buffer, was the FIFO empty when it was queued (queue VI > prev predicted end)?
Hypotheses / outcomes:
- H-dma: a model end_k = max(q_k, end_{k-1}) + D reproduces retail's per-VI buffer counts (residual ~0) -> implement
  ROGUESQ_AI_VI_CLOCK=3 (events.cpp: posts at modelled ends, q_k from osAiSetNextBuffer in ai.cpp) and rerun b17 p1.
- H-const: retail never has empty-FIFO gaps -> the wander is in D (integer cps changes with VI delay) -> model D per VI mode.
- H-unmodelable: queue rows lack the timing resolution to model it -> close g3 det sweep as timing class (s7863 stands).
Budget: this slug's runs so far all discriminated; 2 more iterations max before closing as harness-only.
