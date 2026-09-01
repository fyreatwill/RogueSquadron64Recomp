# M5 Session 3495 — selector comparison blocked by port route

The independent retail arm passed its same-run whole-RDRAM positive control
(10,000 callbacks), reached title origin `0x00790400` at width 1024, and
recorded 156 selector-PC rows in the captured title window. All 78 sampled
`0x80091060` loads returned index `0x00000004`; all 78 paired
`0x80091074` rows returned source `0x80173B20`.

The first port invocation did not qualify the route: it recorded 48 audio
dispatch rows but zero title origins, selector controls, or selector rows. A
fixed direct-PID retry of the same real-audio/LLE/spin-yield recipe also failed
before title, with zero selector controls/rows and a crash at guest PC
`0x8000834C` in the width-640 scheduler/audio path. The retry was killed with
SIGKILL after capture.

The selector parity/source-divergence comparison is therefore unevaluable;
the retail rows are not a valid A/B against the failed port route. This
iteration selects a transient route-qualification blocker and rules out only
an absent retail selector observation. It does not select selector parity,
source divergence, or a selector-route null in the qualified port path.

Evidence: `scratch/agent/s3495_m5_selector_comparison/retail.log`,
`port.log`, and `port-fixed-184117.log`.
