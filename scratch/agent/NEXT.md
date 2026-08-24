# NEXT work unit (s2320) — independent slot active-byte writer census

HYPOTHESIS-ID: m5-status-writer-ground-truth

## Work unit

Run one ground-truth-first explicit keycode-36 staged pair using the existing
stub and Factor 5 image arms. Extend the retail oracle with five physical
active-byte watches for the five-slot table rooted at `0x80154620` with
stride `0x1228`: `0x154620`, `0x155848`, `0x156A70`, `0x157C98`, and
`0x158EC0`. Keep the all-fifteen phase buckets, whole-RDRAM/gate/task/wait
controls, and the existing port slot/key-on/descriptor logger from s2319.
This is an oracle/launcher change only; make no runtime, slot, wait, gate,
guard, consumer, or default change.

## Competing hypotheses and discriminating measurement

- H-Port-Contract-Or-Address: retail writes one or more active bytes in a
  target phase with a named PC and values including `01/02/00`, while the port
  remains at the sentinel key-on row and has no slot-byte/descriptor row. The
  missing edge is a port contract/address mismatch, not a route null.
- H-Retail-Status-Elsewhere: whole-RDRAM, lifetime, target-phase, and port
  controls are positive, but none of the five independent active-byte watches
  has a writer/value row. The retail status writer is elsewhere or outside
  this active-byte ring.
- H-Slot-Transition: retail and port both show named, phase-aligned active
  byte/status transitions with downstream task/PCM ordering.
- H-CoverageInvalid: whole-RDRAM, all fifteen phase buckets, title/hangar, or
  either port arm’s task/PCM controls is absent; no slot null is evaluable.

The discriminator is one table per active-byte watch and arm containing
phase, writer PC, post-value, and `01/02/00` counts, joined to the port
`[slot-alloc]`, `[slot-sb]`, `[init-desc]`, `[keyon-w40]`, task/DMA, and
PCM markers. The whole-RDRAM watch, existing gate/task/wait watches, and
`[vi-callers]` control must be positive in the same capture.

## Exact commands

1. Use `apply_patch` to add these five oracle watches after the existing wait
   watch in `scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh`:

       --watch-write 0x154620:0x154621 \
       --watch-write 0x155848:0x155849 \
       --watch-write 0x156A70:0x156A71 \
       --watch-write 0x157C98:0x157C99 \
       --watch-write 0x158EC0:0x158EC1

   Extend `--first-watch`, `--pc-hist-watch`, and `--post-value-watch` to
   include watch indexes `4` through `8`. Do not remove any existing watch or
   phase bucket.

2. Run:

       zsh -n scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh
       zsh scratch/agent/run_s2317_m5_gate_task_wait_explicit_pair.sh s2320_m5_status_writer_ground_truth

3. Parse only bounded oracle shutdown rows, the driver gate/arm summary, all
   fifteen phase rows, the five new watch tables, and per-arm phase/slot/
   task/PCM marker counts. Require whole-RDRAM `10000+`, fifteen positive
   buckets, title/hangar, and both port hangar phases before interpreting a
   null. Do not change behavior from any null result.
