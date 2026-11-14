# NEXT (s7334): item 24(b) — class the above-sentinel FIFO region instead of "freed"
HYPOTHESIS-ID: hostmap-carve-blind
Context: s7333 closed (a) (abort route FIFO-in-carve host-live 17/17, tools/s7333_carve_report.py). (b): every above-heap FIFO starts
0x10 past an arena end sentinel (fl=8 sz=0): 80904000, 80986800, boot 80B77800 at sentinel+0xD810. rs64_s7325_gap classes it 3
(inside a freed block: stale history) or 4.
Hypotheses: H-trim (the scene setup sets the arena end below the FIFO/fb region on purpose, so the memory above is a static non-heap
carve: the sentinel writer is in the same coalesceFreeHeapBlocks / buildHeapFreeList(lo, hi) call, hi = sentinel), H-top (the region
is the RAMTOP tail osMemSize - fb, always the same physical span per scene), H-stale (a real freed block still covers it, and a
write there after the free would be dangling).
Measurement (offline first, ONE build if needed): from scratch/s7326/s7333_keepv2/run.log, compare each sentinel address to the
"[s7325] heap rebuild ... range=lo..hi" hi values and to the preceding carve end. If sentinel == rebuild hi, H-trim. Then add class
5 "above arena end sentinel (guest non-heap)" in rs64_s7325_gap (computed from the guest walk's sentinel, ahead of the freed-history
check), make tools/s7331_reset_writer_report.py and s7333_carve_report.py print it, and rerun ONE abort route:
`env ARMS=keepv2b zsh scratch/s7333/run2.zsh` (edit ARMS name). Target: 0 FIFO transitions classed 3/4; report rc 0.
If (b) closes, item 24 is closed: take the next CURRENT-TRUTH item / ITERATION 3c rung.
