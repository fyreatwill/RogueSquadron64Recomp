# M5 s3530 selector source writer

The independent retail oracle was run before the port capture with a
whole-RDRAM positive control and a physical watch on `0x165ED0`. It reached
the target route and reported `0x80091CC8` among the phase-gated writers of
that word; the prior qualified retail load at `0x8009192C` was `0x561F`.

The Debug build added a regeneration-safe witness at the generated
`0x80091CC8` store. The retrying real-audio/LLE/spin-yield/autopilot port run
passed title 1024 and hangar 512. In both target phases the witness fired with
`addr=0x80165ED0`, `value=0x5622`; the following input load and downstream
producer, allocator, and selector-store controls were live.

This selects the setup-writer/input divergence at the qualified scope and
rules out a later load-only or allocator explanation. The retail writer watch
did not dump the written value, so the numeric retail-vs-port writer-value
comparison is single-source; the independent line is retail writer-PC presence
plus the already qualified retail load value.

ORIGIN: diagnostic-only writer/store observation. The store is a legitimate
audio-frequency setup write; no audio, selector, task, or output state was
rewritten.

Captures: `scratch/agent/s3530_selector_input_source_oracle/run.log`,
`scratch/agent/s3530_selector_input_source_port/run_retry.log`.
