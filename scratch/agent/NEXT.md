# NEXT work unit (s2291) — M5 Step 3 retail/port image-output writer join

HYPOTHESIS-ID: m5-step3-retail-port-writer-join

## Work unit

Run one ground-truth-plus-port comparison using the now-qualified default
image route. First arm the retail oracle with a positive whole-RDRAM watch and
an output-candidate watch covering the qualified port phase-10 destinations
(`0x166000:0x16A000` physical). Then run the unchanged port default arm with
the established eleven process-start Start events and the image/task/PCM
instrument table. Do not implement a writer, writeback, consumer, slot, gate,
guard, or address remap.

## Competing hypotheses and discriminating measurement

- H-RetailSameWriterSpan: with all retail controls valid, the candidate-span
  watch records writes whose physical destination, byte count, writer-PC class,
  and payload polarity agree with one of the port's nonzero phase-10
  `audtask-image-stage`/DMA rows. This selects one shared output contract edge.
- H-RetailDifferentWriter: retail reaches title/hangar and writes the
  candidate span, but its writer PC, span, payload polarity, or ordering does
  not match the port row. This selects a contract-class difference, not a
  mitigation target.
- H-RetailDifferentAddressClass: retail passes the controls but produces no
  candidate-span write while its independent output/task watch remains active.
  This selects an address-class difference at this watch scope; it does not
  prove the port writer is wrong.
- H-CoverageInvalid: the oracle whole-RDRAM/title/hangar controls or the port
  input/title/hangar controls are absent. No writer or output null is
  interpretable.

The discriminator is the joined table `(phase, origin, destination span,
length, writer PC, payload nonzero/polarity, ordering)`, with the oracle's
whole-RDRAM threshold and title/hangar rows as positive controls. A retail
candidate hit plus an exact port row selects H-RetailSameWriterSpan; a
controlled candidate hit with a mismatch selects H-RetailDifferentWriter; a
controlled zero candidate watch with a separate active output/task watch
selects H-RetailDifferentAddressClass; any missing control selects
H-CoverageInvalid.

## Exact commands

1. Build once:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

2. Create the self-contained driver
   `scratch/agent/run_s2291_m5_writer_join.sh`. It must launch the retail
   oracle before the port arm, retain the whole-RDRAM positive-control result,
   use `--watch-write 0x166000:0x16A000` plus bounded writer-PC/phase output,
   gate the port on explicit Start delivery and title/hangar VI rows, and
   SIGKILL every remaining process in cleanup.

3. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2291_m5_writer_join.sh`

   `zsh scratch/agent/run_s2291_m5_writer_join.sh`

If either side misses its positive controls, record H-CoverageInvalid and do
not interpret the candidate-span null. No runtime change is authorized by this
work unit.
