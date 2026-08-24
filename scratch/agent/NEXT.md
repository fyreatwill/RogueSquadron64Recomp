# NEXT work unit (s2323) — close the target status lifecycle boundary

HYPOTHESIS-ID: m5-status-cycle-ground-truth

## Work unit

Add VI ordinal and current origin/width to the oracle's existing
`--status-poll` change rows. Then run the existing explicit keycode-36 staged
stub/image pair once with `--status-poll` and the completed
`--post-value-pc-detail` table. This is oracle instrumentation plus one
ground-truth capture only: do not change port runtime, audio dispatch, slot
writers, gates, waits, consumers, addresses, mitigations, or defaults.

The s2322 ground-truth prerequisite is positive: whole-RDRAM `10329`, title /
hangar, gate/task/wait `17/108/0`, all fifteen phase buckets, and five target
`01/02` rows at physical `0x00154620` owned by `0x8009B214`/`0x8009B6F8`.

## Competing hypotheses and discriminating measurement

- H-Status-Cycle: the target word is a live slot-state word. A phase-keyed
  status-poll table for all eighteen status words shows target top byte
  `01/02` followed by `00`, and the detail rows name the writer for the
  nonzero transition and any zeroing transition.
- H-Status-Sticky: the target word reaches `01/02` but never returns to
  `00` during the qualified target/hangar window. The status-poll table has
  no target zero transition despite positive coverage.
- H-Status-Other-Word: `0x00154620` is not the lifecycle word; another one of
  the eighteen polled words supplies the complete `01/02/00` sequence or the
  target poll remains unchanged while detail rows vary.
- H-CoverageInvalid: whole-RDRAM, title/hangar, gate/task/wait, one or more
  phase buckets, or either port arm's task/PCM controls is absent.

The discriminator is one same-run table keyed by
`(slot/address, VI ordinal, origin, width, top byte)`, joined to every
`post-value-pc-row` by the same VI/origin/width/address fields. Do not use
wall-clock timing. A complete target `01/02 -> 00` join selects
H-Status-Cycle; a positive target capture without zero selects
H-Status-Sticky; another word's complete sequence selects H-Status-Other-Word;
missing controls selects H-CoverageInvalid.

## Exact commands

1. Use `apply_patch` in `tools/oracle/rs64_oracle.c` at the `vi_poller`
   `oracle-status-poll` print to include `vi=g_vis`, the sampled VI width, and
   the sampled VI origin. Preserve the existing eighteen-word polling and
   change-only behavior.
2. Build and syntax-check:

       ./tools/oracle/build.sh
       zsh -n scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh

3. Use `apply_patch` to add `--status-poll` immediately after `--vi-trace` in
   `scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh`, syntax-check,
   and run:

       zsh scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh s2323_m5_status_cycle

4. Parse only the bounded `oracle-status-poll`, `post-value-pc-row`,
   `post-target-*`, fifteen `pc-hist-phase`, watch-write, driver-arm,
   slot/key-on, task/DMA, and PCM rows. Report the phase-keyed top-byte
   sequence for `0x00154620` and every competing status-word sequence, then
   select exactly one hypothesis. Do not change behavior from the result.
