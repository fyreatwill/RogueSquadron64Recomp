# NEXT (s7446)
HYPOTHESIS-ID: default-diag-bursts

Class DC (CURRENT-TRUTH Next steps item 1): the [spill] allocation log. After s7445 it is the only non-PERSISTENT tag in
the default-arm stderr (scratch/s7445/run_default.tlog: 757 lines / 41.7 KB, all in ONE second at t=12.4 s, lines like
"[spill] req=0x18 -> 81000000 (used 0x20 live 0x20)"). Emitters: grep -n '\[spill\]' src/main/upstream_compat.cpp
(s6569 bump, s6702 reuse every 256th, s7326 "arena full" - the arena-full line is a crash breadcrumb and must stay).
Hypotheses: H-needed (the per-request lines are the s6858/s7326 heap triage's only record of where spill blocks land: keep,
maybe budget), H-hidden (per-request lines latch on a consumer env such as ROGUESQ_S7317_ALLOCMAP / a new ROGUESQ_SPILL_LOG=1,
G1E_TRIM=0 old, arena-full + reuse summaries stay), H-clean (one-time load list, 41 KB, leave it and close the class audit).
Measure: env S7431_ARM=DC zsh tools/s7431_stderr_volume.sh 150 -> [spill] per-request 0, arena-full path untouched; consumer
control with the env must print them (same count, 757). If DC closes, the default-diag audit campaign is done: take
CURRENT-TRUTH item 2 onward.
