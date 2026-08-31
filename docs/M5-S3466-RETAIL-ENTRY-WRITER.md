# M5 Session 3466 — retail source-table entry writers

The independent Rice oracle was run with the whole-RDRAM write control, the
physical source-slot watch, the title phase gates, and a physical watch on the
observed table-entry span `0x001B4AA0:0x001B4B24`.

The corrected 35-second capture passed the controls: whole-RDRAM writes
14,948, source-slot writes 1,916, title phase 535 VI frames, and table-span
writes 3,032. The existing execution watches fired 2,619 times at
`0x800644A8`, 7,479 times at `0x800644DC`, and 7,186 times at `0x80064524`.

The table-span writer histogram identifies title-phase writers at
`0x80064350`, `0x80064360`, `0x80064378`, `0x800646D8`, plus
`0x800078EC`, `0x80028F30`, `0x80028F40`, `0x80028F90`, and `0x80029034`.
Initialization/copy writers `0x80018F5C`, `0x80018F60`, and `0x80018F80` are
also active. This proves the retail table-entry write route exists and gives
the next candidate PC set; it does not yet attribute one stored value to one
load row because detailed write rows expose address and PC, not the written
word.

The title load rows still select entries such as `0x801B4AA0` and
`0x801B4AA8`, while the shared store receives nonzero state pointers. The
positive controls fired in the same run, so the null interpretation is not
available. The 90-second first attempt was invalid because the oracle stopped
before flushing its summary during the later attract transition; the
35-second retry and detail capture corrected that setup issue.

Evidence: `scratch/agent/s3466_m5_retail_entry_writer_retry/oracle.log` and
`scratch/agent/s3466_m5_retail_entry_writer_detail/oracle.log`.
