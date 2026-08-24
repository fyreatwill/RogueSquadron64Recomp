# NEXT work unit (s2292) — M5 Step 3 all-ring-slot retail payload attribution

HYPOTHESIS-ID: m5-step3-retail-port-writer-join

## Work unit

Run one ground-truth-plus-port comparison that splits the candidate span into
all observed `0x300` Factor 5 ring slots. Keep the independent whole-RDRAM,
task/output, title, hangar, and explicit-Start controls. Arm bounded writer-PC
and post-value summaries for every slot from `0x166450` through `0x169150`;
run the unchanged default image route and do not implement a writer,
writeback, consumer, slot, gate, guard, or address remap.

## Competing hypotheses and discriminating measurement

- H-RetailPayloadWriterMatch: one exact ring-slot watch records post-target
  retail stores with a writer PC, `0x300` span, nonzero payload, and ordering
  that match a port nonzero phase-10 image-stage/DMA row. This selects the
  shared payload contract edge.
- H-RetailMetadataOnly: the exact slot watches remain active, but retail rows
  are pointer/length metadata or otherwise do not supply the port payload
  tuple. This selects the remaining retail-to-port contract gap, not a guard or
  writeback fix.
- H-RingRotationUnresolved: the broad candidate watch and all controls pass,
  but no single pre-armed ring slot overlaps the port's nonzero row. This
  proves only that the ring address is dynamic at this recipe scope and keeps
  the payload writer open.
- H-CoverageInvalid: any whole-RDRAM, retail title/hangar, or port
  title/hangar/Start control is absent; no narrow null is interpretable.

The discriminator is one table keyed by `(slot, phase, origin, retail writer
PC, destination, length, post-value/polarity, port DMA FNV/nonzero,
source-before-consumer, completion ordering)`. A matching exact slot selects
H-RetailPayloadWriterMatch; active controls plus metadata-only rows select
H-RetailMetadataOnly; active controls with no slot overlap select
H-RingRotationUnresolved; missing controls select H-CoverageInvalid.

## Exact commands

1. Build once:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

2. Create the self-contained driver
   `scratch/agent/run_s2292_m5_all_ring_writer_join.sh`. It must launch the
   retail oracle first, use watch index 0 for `0x0:0x800000`, index 1 for
   `0x166000:0x16A000`, index 2 for `0x141AD0:0x141AF0`, and indexes 3–18 for
   `0x300` windows beginning at `0x166450` and increasing by `0x300` through
   `0x169150`. It must retain the oracle shutdown summaries, gate the port on
   explicit keycode-36 Start delivery plus title/hangar VI rows, and SIGKILL
   every remaining process in cleanup.

3. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2292_m5_all_ring_writer_join.sh`

   `zsh scratch/agent/run_s2292_m5_all_ring_writer_join.sh`

If either side misses a positive control, record H-CoverageInvalid and do not
interpret any ring-slot null. No runtime behavior change is authorized.
