# Session 3330 — M5 slot/status qualification

The prescribed port image-arm run used phase-gated capture at VI-512 with
`60:start,90:start,120:start` relative to the phase. It reached VI-1024 at
the title and VI-512 at `0x006AB400` after 93.9 s, then captured 125 frames
before the process aborted at 146.5 s after startup. The positive controls
were live in the target phase: 5,082 `audtask-dma-row` entries, 13,499
`audtask-join` entries, 7,148 PCM source entries, 7,130 PCM consumer entries,
and 4 voice-probe rows including the initial arm row.

The port log contained zero slot/status rows and zero executions of the named
retail consumer PCs `0x80094648`, `0x8009B600`, `0x8009B85C`, and `0x8009BDE8`.
The actual MusyX voice probe remained `max=1 active=0 mask=0x00000000`; the
other count remained the cinematic dispatcher pool and was not observed in
this run's voice probe. This selects `H-PortSlotStatusMissing` for the
reachable hangar recipe. It does not identify the missing writer or authorize
an audio contract change; evidence is single-source on the port side and must
be paired with the existing independent retail capture before implementation.

The process later hit the known abort path: `do_rom_read` asserted on an
unaligned ROM address in `pi.cpp:86`, with last guest PC `0x80001B08`. That
abort occurred after the target controls and does not invalidate the bounded
slot/status result.
