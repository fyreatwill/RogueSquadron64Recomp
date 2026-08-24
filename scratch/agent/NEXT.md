# NEXT work unit (s2324) — unlock the parked M5 key-on tuple boundary

HYPOTHESIS-ID: m5-keyon-tuple-contract

## Work unit

Parked pending a genuinely new route discriminator that restores the qualified
`512 @ 0x006AB400` target window. Do not repeat the status-cycle capture, the
existing explicit keycode-36 schedule, or the failed C88/A1 matrices. Do not
change port runtime, audio dispatch, slot writers, gates, waits, consumers,
addresses, mitigations, or defaults.

The next runnable unit must first establish a new within-run route arm that
restores target coverage, then collect the existing key-on/slot/descriptor,
task/DMA, PCM, route-state, and phase controls for all arms in one build. Until
that discriminator exists, no build or game run is authorized for this thread.

## Competing hypotheses and discriminating measurement

- H-Port-Route-Gap: the port's route/input state still prevents the target
  hangar contract; the new arm restores `512 @ 0x006AB400` and changes the
  route-state/key-on tuple before slot allocation.
- H-Port-Slot-Contract: the target phase is restored but the port still has no
  status/descriptor writer; target coverage is positive while slot allocation,
  descriptor, and key-on rows remain zero/sentinel.
- H-Port-Audio-Arm: stub/image dispatch changes the missing key-on contract;
  both arms must be present in the same run and differ in the downstream slot
  or key-on table, not merely in task/DMA counts.
- H-CoverageInvalid: whole-RDRAM, title/hangar, target phase, or task/PCM
  controls are absent, so no port conclusion is admissible.

The discriminator is one same-run table keyed by
`(arm, route-state, VI ordinal, origin, width, slot/status address, key-on
index, descriptor row, task/DMA tuple, PCM source/consumer tuple)`. A new arm
with target coverage and a changed route tuple selects H-Port-Route-Gap;
target coverage with unchanged zero/sentinel slot rows selects
H-Port-Slot-Contract; an image-vs-stub downstream difference selects
H-Port-Audio-Arm; missing controls selects H-CoverageInvalid.

## Exact commands

No exact build/run command is authorized until the new route discriminator and
self-contained launcher exist. When one is identified, the single work unit
must use this shape from the repository root, with both arms built together:

    zsh -n scratch/agent/<new-route-discriminator>.sh
    zsh scratch/agent/<new-route-discriminator>.sh s2324_m5_keyon_tuple

The launcher must phase-gate on VI transitions, arm the whole-RDRAM oracle
positive control before narrow watches, kill every process group with SIGKILL,
and report the four outcomes above. Do not substitute a stopwatch or another
repeat of the s2317/s2323 recipe.
