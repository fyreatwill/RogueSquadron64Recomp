# NEXT: G5a open question - is block 8074A380 live when RT64 copyNativeToRAM writes it (dd4 16:9)?
HYPOTHESIS-ID: g5a-copynative-live
Context: G5i closed on data s6997 (awaits owner look). Backlog items 2-8 await owner flights; item 2 carries one open
engineering question (PORTING-STATE ~181750): at dd4 16:9 RT64 copyNativeToRAM writes framebuffer pixels onto the watched
word 8074A380/8074AC60 (171 memmove + 171 swap hits, run d4live). If that guest block is a live heap object at the time
(not a framebuffer the game owns), the write is a corruption source of the G5a walker-pointer family.
Hypotheses:
- H-fb: 8074A380 lies inside a colour image the game itself set (SetColorImage range covers it) -> legitimate copy, close.
- H-stale: RT64 copies to a stale/previous colour-image address the game has since freed and reused (heap block live) -> ours, fix.
- H-span: copy width/height at dd>1 or wide overruns the real colour image end into the next block -> ours, clamp.
Discriminator, one build/one run: log every copyNativeToRAM (dst addr, w, h, bytes) alongside the last game SetColorImage
addr/width and the rs_malloc block owning dst (heap walk at copy time). Positive control: the current fb copy (dst = live
colour image) must log as H-fb. Read grep -n "8074A380\|copyNativeToRAM" PORTING-STATE.md | tail first for the d4live recipe.
