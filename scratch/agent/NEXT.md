# NEXT: (optional, low value) Gfx-thread XXH3_hashLong / memmove audit
HYPOTHESIS-ID: gfx-hash-audit
Context (s7069): host-selftime-audit closed. Gfx Thread on-CPU self in the s7069 on arm (scratch/s7069/on, 214 sample dumps,
L6 dd1 4:3 FPS60): factor5_ucode_nmac 29.6% (the LLE ucode, functional), _platform_memmove 8.1% (1136), XXH3_hashLong_64b
7.3% (1021), rsp_dpc_submit_impl 6.5%. AN OWNER REPORT PREEMPTS THIS (CURRENT-TRUTH Next steps 1-12 await owner flights).
Hypotheses: H-tex (RT64 hashes TMEM/texture uploads per load; cost scales with loads, needed for its texture cache) vs
H-redundant (the same bytes are rehashed several times per frame, e.g. per tile or per copyNativeToRAM/framebuffer check, and
can be memoised) vs H-ours (a hash we added in rs64* RT64 glue, e.g. rs64LoadBlockRuns or a frame-diff detector).
Discriminator, NO build first: re-read the existing dumps for the callers of XXH3_hashLong_64b and _platform_memmove
(the `sample` call trees in scratch/s7069/on/smp_*.txt carry full stacks; write a small parent-frame tally, tools/s7070_parents.py).
Caller split decides: RT64 texture cache path -> H-tex (close unless bytes/frame look redundant); an rs64 frame -> H-ours
(gate it like s7068); same call site with many calls per frame of identical size -> H-redundant (memoise, same-build A/B with
an =0 knob, scratch/s7069/both.zsh recipe).
