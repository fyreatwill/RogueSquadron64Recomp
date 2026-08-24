# NEXT work unit (s2326) — M5 destination-to-slot/key-on join

HYPOTHESIS-ID: m5-destination-slot-keyon-join

## Work unit

Build one ground-truth-first table that joins each rotating Factor 5 image
destination to the port's slot allocation/byte, descriptor, voice/filter,
and key-on rows. Run the retail oracle first with the whole-RDRAM control and
the s2325 task/output/status controls, then run stub and image arms from the
same qualified eleven-Start route. This is one measurement; do not change
dispatch, writeback, slot values, guards, gates, waits, or defaults.

## Competing hypotheses and discriminating measurement

- H-Destination-Is-Slot-Input: the exact PCM-joined destination is the live
  slot input. Its `(origin,width,VI ordinal,destination,length,FNV,nz)` row
  is followed by a matching slot/descriptor/key-on tuple and terminal status.
- H-Destination-Role-Skew: the stage-only destination is the slot input or
  alternate role, while the exact PCM-joined destination is not. The two
  destinations have different downstream rows after matching phase and event
  windows.
- H-Missing-Descriptor-Contract: both destinations have task/PCM progress but
  neither has a slot/descriptor/key-on row. This leaves the missing guest
  descriptor or consumer edge as the boundary.
- H-CoverageInvalid: the oracle controls, target VI phase, or either port arm
  is absent; no null or role conclusion is admissible.

The discriminator is one table keyed by `(arm, phase, width, origin, VI
ordinal, task n, image destination, length, stage FNV/nz, stage/complete
events, PCM source/consumer events, slot index/status byte, descriptor
pointer, voice/filter row, key-on tuple, route state)` with event deltas.
An exact destination-to-slot/key-on lifecycle selects
H-Destination-Is-Slot-Input; opposite downstream polarity selects
H-Destination-Role-Skew; target coverage with neither destination producing
the contract selects H-Missing-Descriptor-Contract; missing positive controls
selects H-CoverageInvalid.

## Exact commands

Create the self-contained launcher with both port arms and the oracle gate,
then run it from the repository root:

    zsh -n scratch/agent/run_s2326_m5_destination_slot_join.sh
    zsh scratch/agent/run_s2326_m5_destination_slot_join.sh s2326_m5_destination_slot_join

The launcher must arm whole-RDRAM before narrow watches, retain the retail
`0x80094648`, `0x8008EB8C`, and `0x8008EBBC` writer controls plus gate/task/
status/wait controls, phase-gate all port rows at title/hangar VI transitions,
run stub and image in one build, and emit the complete destination-to-slot
table before classifying the four outcomes. Use SIGKILL for every cleanup.
