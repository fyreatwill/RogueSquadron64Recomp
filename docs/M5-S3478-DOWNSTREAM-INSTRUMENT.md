# M5 Session 3478 — downstream boundary instrument

The independent retail preflight used the whole-RDRAM positive control and
reached title origin `0x00790400` at width 1024. The six selected late
`rs_free` PCs were absent in that title-gated capture, while `0x80033410` was
active; this is route-qualified ground truth, not a claim that the six PCs
are globally dead.

The port build succeeded with new phase-gated post-call `osSendMesg` and host
audio-task enqueue/output observations. Three port attempts stopped in the
640 phase, so none reached the title gate and the new rows were zero. The
port null is unevaluable and selects no hypothesis. The host hook is
observation-only and does not rewrite or validate guest values.

Evidence: `scratch/agent/s3478_retail_preflight_fixed.log`,
`scratch/agent/s3478_port_downstream_paced.log`.
