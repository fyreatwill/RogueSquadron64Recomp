# NEXT work unit (s2321) — phase-keyed active-byte writer/value join

HYPOTHESIS-ID: m5-status-writer-ground-truth

## Work unit

Run one ground-truth-first explicit keycode-36 staged pair using the existing
stub and Factor 5 image arms. Keep the five active-byte watches and all
fifteen phase buckets from s2320, but add `--post-value-pc` for every named
active-byte writer observed there plus the prior known `0x8009B2C4` control.
This makes the post-store values phase-keyed through the oracle's bounded
`post-target-row-final` table. Keep the whole-RDRAM/gate/task/wait controls,
the existing port slot/key-on/descriptor logger, and all task/DMA/PCM
markers. This is an oracle/launcher change only; make no runtime, slot, wait,
gate, guard, consumer, address, or default change.

## Competing hypotheses and discriminating measurement

- H-Retail-Nonzero-Target: a requested active-byte writer produces a row at
  `origin=0x006AB400 width=512` whose aligned post-store word has top byte
  `01` or `02`. With the port still at sentinel key-on and no descriptor,
  this selects a port contract/address mismatch.
- H-Retail-Zero-Target: named target-phase writers produce only top-byte `00`
  rows, with no `01/02` target row. The retail stores are housekeeping or
  reaping, not the missing active transition.
- H-Retail-Earlier-Nonzero: top-byte `01/02` rows occur only in another
  observed VI-origin bucket, not in the hangar target bucket; the unresolved
  boundary is phase/route timing rather than the five-address choice.
- H-CoverageInvalid: whole-RDRAM, all fifteen phase buckets, title/hangar, or
  either port arm's task/PCM controls is absent; no value null is evaluable.

The discriminator is one complete table of `post-target-row-final` rows keyed
by requested writer PC, watch address, phase origin/width, and aligned word.
Decode the active status as `(value >> 24) & 0xff`; lower-field nonzero values
do not count as status transitions. Join the result to the port
`[slot-alloc]`, `[slot-sb]`, `[init-desc]`, `[keyon-w40]`, task/DMA, and PCM
markers. Require the whole-RDRAM control, gate/task/wait controls, all fifteen
phase rows, `[vi-callers]`, title/hangar, and both port hangar phases before
interpreting any null.

## Exact commands

1. Use `apply_patch` to add this single oracle argument after the existing
   `--post-value-watch` arguments in
   `scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh`:

       --post-value-pc 0x8009BBF0,0x8009B170,0x8009B174,0x8009B178,0x8009B214,0x8009B6F8,0x8009B7CC,0x8009B7EC,0x8009B2C4,0x800292E4,0x800298E0,0x80017DB0,0x80015BC8,0x80022B1C

   Preserve every existing watch, phase bucket, and port environment.

2. Run:

       zsh -n scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh
       zsh scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh s2321_m5_status_writer_phase_value_join

3. Parse only bounded oracle shutdown rows matching `post-target-row-final`,
   `post-target-summary`, `post-target-class`, the fifteen `pc-hist-phase`
   rows, and the watch-write totals, plus the driver gate/arm summary and
   per-arm slot/task/PCM markers. Report top-byte `01`, `02`, and `00` counts
   separately for `0x006AB400:512` and all other buckets. Do not change any
   behavior from a zero-only or missing-writer result.
