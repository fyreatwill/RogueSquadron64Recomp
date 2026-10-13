# Find the writer of the corrupt synth list link (0x94FC)

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4778: +5808 == guest 0x80091368 `lhu $v0,0x10($v1)` in the list walk 0x80091368-0x80091380; $v1=0x94FC (non-pointer), reached via `lw $v1,0($v1)` at 0x80091378 (or the head).
Use the existing rs64_s4307_synth_read hook: log (node, next) for each 0x80091378 read in the last frame before the crash, and identify the node whose +0 holds 0x94FC. Then watch stores to that node (rs64_m5_lowfield_store / writer_parity) for the writer PC.
Positive control: same log on a non-crashing frame shows valid KSEG0 chains. Map asm via `cd build && make <path>/funcs_24.c.s` (no lldb needed).
Write ORIGIN: in the session entry if a guard is added.
