# M5 Session 3420 — retail writer-loop entry arguments

The retail oracle ran the validated Rice/Start route for 50 seconds with a
whole-RDRAM positive control, the target-span watch, the producer execution
watch, and a bounded target-store field dump. The run exited cleanly with
11,166 whole-RDRAM writes, 1,166 target-span writes, and 1,289,923 producer-PC
execution hits.

All 664 target-span writes attributed to `0x800078EC` had the same entry
tuple:

    a0=0x801797B0 a1=0x00000000 a2=0x00000298 ra=0x8008F2D4

The target-store field capture reported width 1024 and origin `0x006AB800`
for every row. The earlier 512 phase bucket was not the callback's live phase
and produced a false gate zero. Post-store sampling remained mixed, with 65
nonzero bytes in the final sampled range.

This selects `H-RetailEntryZero`: retail enters the same zero-fill tuple as
the port at the observed boundary. It refutes `H-RetailEntryNonzero` and
closes the entry-argument explanation for the missing port payload. The next
discriminator must compare state inside the writer loop or the subsequent
publication path; this does not establish that the shared zero entry is
legitimate for the port.

Evidence: `scratch/agent/s3422_retail_entry_arguments_capture/oracle.log`.
