# M5 s3413 — retail source-span ground truth

The prescribed Rice-plugin oracle arm exited with code 138 after 24.7
seconds of wall time during shader compilation. Its log contained 117 GLSL
undeclared-identifier errors and no completed phase or payload summary.

The falsifiable repair used the identical watches with the installed
Glide64mk2 plugin. It completed the full 120-second window and emulated 7,171
VI frames. The whole-RDRAM positive control reached 10,000 writes and was
removed; the producer execution watch at `0x800078EC` reached 9,667 hits.
The requested physical source span `0x1797B0:0x179A48` had zero writes. The
producer execution summary reported `prev=0x800078EC` for all 9,667 hits.
The oracle emitted no phase-qualified source-span rows, so the hangar-bucket
classification is unevaluable. This is a valid global negative at the
observed route, not evidence that the port's zero span is legitimate or that
retail never writes a corresponding destination in a different region.

The result rules out neither a retail producer absent from this span nor a
retail destination mismatch. No port code, waits, slots, dispatch, or PCM
writeback changed. Evidence: `scratch/agent/s3413_retail_source_span/oracle.log`
and `scratch/agent/s3413_retail_source_span_glide/oracle.log`.
