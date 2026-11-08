# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: name the source of tlut id 0x1058 on the ltex_cache records at 21:9 (level 15 crash, s6991), then fix it
HYPOTHESIS-ID: l15-219-tlut-oob
State (s6991): L15 dd4 21:9 crashes 6/6 at t~97. Chain: loadLevelTextureCache 0x8004836C stores desc+6 = getTextureAttrBySlot(id) =
record+0xE = 0x1058 for the 4 "ltex_cache_N" records, and the texture tables are built with 2000 slots at 21:9 (2048 at 4:3/16:9).
The worker 0x800496A8 then copies the TLUT to table[4184], which sits inside the material pool, so the free list is corrupted.
Hypotheses:
- H-stale: nothing stores 0x1058. loadTextureToMemory keeps the old +0xE when the caller passes a TLUT id != 0xFFFF, and
  init zeroes only record+0. At 4:3/16:9 the same leftover happens to be a valid id (65-70?). Fix: initialise +0xE to
  0xFFFF on fresh records, or make ltex_cache take the alloc path, in a fixup patch, default on, with =0 restoring old behaviour.
- H-path: a 21:9-only path (our G1d config: 1024-wide framebuffer, other bADM args) writes 0x1058. Name it and fix it there.
- H-layout: the 2000-slot layout (buildAndRegisterDefaultMaterial arg 0xB6(sp)) is the bug, e.g. our 21:9 code picked the
  game's hi-res video config. Then 2048 at 21:9 might cure it.
Unit, one build, one instrument: in tools/apply_s6992_matwatch.py add a fixed watch on record 0x8017B790 +0x0C..+0x10
(deterministic at 21:9; print pc/fn/value for every store), and run with ROGUESQ_BUCKETLOG=1 too (rs64_s6090_init logs
a0/a1/ra of every initTextureLUTAndAllocBuffers call). Arms in scratch/s6992/arms.sh (T4_169 and T4_219; drop T1_43 to save time).
At 16:9, read the record address off [tlutw]/[matw-rec] (the [matw-rec] print only fires on a pool hit, so print the
record from s6992e as well).
Expected: a 0x1058 store at 21:9 -> H-path names the writer. No store -> H-stale. The init a0/a1 differ by aspect -> layout
source named (bADM caller advanceVideoFrame/initVideoBootWrapper args).
Positive control: [descw2]/[tlutw] must fire at 21:9 (they did 6/6), and the record-watch must see the 0x0820 store at +0xC.
Then land the fix and qualify it: L15 21:9 dd4 hold >=200 s with 0 crash, oob=0, plus a 16:9 arm unchanged.
Host: the harness exits 2 on human input (idle < 120 s). Check `ioreg -c IOHIDSystem` idle first.
After that: re-run the real 16:9 per-level sweep (s6990 flew level 1 x19): scratch/s6991/drive.sh with ASPECT=16:9.
