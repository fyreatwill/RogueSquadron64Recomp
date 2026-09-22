# M5 s3739 — port entry/setup census

The batched capture retained the independent retail oracle, whole-RDRAM
positive control, real-audio port arm, silent audio control, both source
watches, and both VI phase gates. The oracle control fired and reached title
and hangar. The real port reached title and emitted the qualified source-DMA
rows; the silent arm reached title but emitted no source-DMA rows. Neither
port arm crashed.

The real port did enter both candidate families: `0x80007670` appeared in
300 producer rows and `0x8001E2C0` in 19. Their measured target-span rows
were pre-route setup activity, not hangar-qualified rows: `0x80007670` had
54 nonzero byte values and 246 zero values, while `0x8001E2C0` had 19 zero
values. The same family-entry counts occurred in the silent control, so these
entries are shared setup activity and do not explain the real-audio source
route. The real hangar source-range writer still emitted 512 rows, all with
zero payload (`payload_nz=0`, `FNV=0x762B22A5`), and the input-DMA rows still
identified the legitimate `0x800078EC` zero fill as the previous writer.

This refutes `H-PortFamilyNeverEntered` for the measured entry hook and
refutes a simple missing-destination explanation: both families execute and
touch the source span. It also refutes `H-PortFamilyWritesThenClear` for the
qualified hangar path because no nonzero family output reached the real
source-range writer. The result is narrower than the original three-way
split: family entry exists, but its value/setup provenance is not yet joined
to the qualified route. No behavior or writer was changed.

Evidence: `scratch/agent/s3739_m5_port_entry_setup/summary.txt`, `real.log`,
`silent.log`, and `oracle.log`.
