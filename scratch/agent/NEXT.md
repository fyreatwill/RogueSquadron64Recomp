# NEXT work unit (s2322) — identify the earlier nonzero status writer

HYPOTHESIS-ID: m5-status-writer-ground-truth

## Work unit

Add one bounded detail table to the retail oracle's existing
`--post-value-pc` path. For every requested writer-PC post-store sample,
record `(writer PC, VI ordinal, live origin/width, aligned watch address,
aligned value)` before the current target-origin filter. Keep the existing
`post-target-*` table, all five physical watches, all fifteen phase buckets,
the whole-RDRAM/gate/task/wait controls, and the explicit keycode-36 stub/image
pair. This is an oracle instrumentation change only: no port runtime,
audio, slot, gate, wait, consumer, address, mitigation, or default change.

The existing s2321 oracle capture is the ground-truth prerequisite for this
instrument: it passed the whole-RDRAM positive control and showed that the
missing information is writer/value ownership, not lack of phase coverage.

## Competing hypotheses and discriminating measurement

- H-Earlier-Status-Writer: the non-target top-byte `01/02` values are emitted
  by one of the fourteen requested active-byte writer PCs. The detail table
  must show the writer PC, physical watch, and phase origin for each value.
- H-Earlier-Other-Writer: the non-target `01/02` values are emitted by a
  different writer PC or a different watched word; the requested-PC detail
  rows contain no such values.
- H-Target-Status: a detail row at `origin=0x006AB400 width=512` has top byte
  `01` or `02`, overturning the s2321 target absence.
- H-CoverageInvalid: the whole-RDRAM threshold, all fifteen phase buckets,
  title/hangar, or either port arm's task/PCM controls is absent.

The discriminator is one complete `post-value-pc-row` table keyed by
`(writer PC, origin, width, watch address, value)`. Decode only
`(value >> 24) & 0xff`; lower-field nonzero values do not count as status.
Require the same-run positive controls and join the result to the port
`[slot-alloc]`, `[slot-sb]`, `[init-desc]`, `[keyon-w40]`, task/DMA, and PCM
markers before selecting an outcome.

## Exact commands

1. Use `apply_patch` in `tools/oracle/rs64_oracle.c` to add an opt-in
   `--post-value-pc-detail` flag and a bounded detail-row array. In the
   post-step block that currently calls `record_post_value_requested_sequence`,
   `record_post_value_requested_class`, and
   `record_post_value_requested_row`, append one detail row for every
   `g_post_value_pending_target >= 0` sample using the pending PC, VI, width,
   origin, aligned address, and post-step value. Do not change the existing
   target-origin filter or breakpoint/step behavior. At shutdown print one
   row per detail sample as:

       [oracle] post-value-pc-row pc=0x%08x vi=%ld width=%u origin=0x%08x addr=0x%08x value=0x%08x

   only when the new flag is present. Add the flag to the usage text.

2. Build only the oracle front-end and verify syntax:

       ./tools/oracle/build.sh
       zsh -n scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh

3. Use `apply_patch` to add `--post-value-pc-detail` immediately after the
   existing `--post-value-pc` argument in
   `scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh`, then run:

       zsh -n scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh
       zsh scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh s2322_m5_status_writer_value_owner

4. Parse only the bounded `post-value-pc-row`, `post-target-*`, fifteen
   `pc-hist-phase`, watch-write, driver-arm, slot/key-on, task/DMA, and PCM
   rows. Report target versus non-target top-byte `00/01/02` counts and the
   writer-PC/physical-watch owner of every `01/02` row. Do not change behavior
   from the result.
