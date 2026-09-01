# M5 session 3542 — port zero-fill writeback origin

Static enumeration identifies `0x800078EC` as the `sb` inside `rs_memset`,
whose callers invoke `jal 0x800078E0`. One same-build real-audio
LLE/spin-yield/autopilot capture added a phase-qualified entry witness.

The capture passed controls: it reached title VI 1024 at `0x00790400` and
hangar VI 512 at `0x006AB400`; field-writer controls, RSP-source controls,
image-stage rows, and downstream joins were live. The source clears were:

```
phase=4 width=1024 origin=0x790400: rs_memset(dst=0x80178C80, fill=0, len=0x298)
phase=5 width=512  origin=0x6AB400: rs_memset(dst=0x801797B0, fill=0, len=0x298)
```

The byte loop emitted the selected zero stores at `0x178C80`; the 0x298-byte
zero payload has FNV-1a `C0EFD6A5`. Candidate scalar-store and host memset
hooks were silent because this is the generated `rs_memset` body itself, not a
host `memset` call. Its generated wrapper reports `ra=0`, so the static `jal`
census—not that wrapper return address—is the caller evidence.

This selects `H-WritebackOrigin`: the port zeroing is a concrete generic
byte-clear operation at the source-range destination, not an unattributed DMA
write or a mismatched per-byte hook. It explains why the downstream image task
sees zero source bytes. It does not explain why the range is empty before this
clear, so no audio or output state was changed.

Evidence: `scratch/agent/s3542_m5_writer_origin/port.log` and the static
`../N64Recomp/RecompiledFuncs/funcs_2.c` caller census.
