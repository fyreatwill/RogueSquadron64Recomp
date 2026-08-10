# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s624 recap (read this first)

**-385 M1 LIVE-VERIFIED on recovery-active class-D.**

### Scored SCORE (s624 att7)
- force6=1 force_old5=1 BASE_CTRL_PASS case5_n0_state=5
- recov768=7952 thr11d_new=1 sec4_post=1 cshadow_a=3 ltex=1
- **ltexmg=1 ltex_null=0 thr12_post=0** class_hint=M1_ltexmg_no_thr12
- Tag: `[level-tex-malloc-guard] n=0 bad_s0=0x00000000 size=0x136C`
- Crash residual **-387** (1×): `do_rom_read+608` ← submitDmaSlot ← processAssetLoadStep
  ← mainEventQueueWorker; si=`0x380000003`; last-guest-pc `0x800290d4` STALE (-259)

### Soak policy CONFIRMED
- H-recovwait1: recovery ~+22s post hsel → RECOV_WAIT_S=50
- Prefer BUDGET_S≥900 when pre-eng 128s `setByteAcrossVertexList`/`0x800aafa8` is frequent

Full: CURRENT-TRUTH -387/-385; PORTING-STATE Session 624.

## This iteration's work unit

**Why `rs_malloc(0x136C)` returns null (H-ltexOOM) — heap free-head / size instrument.**

1. Locate `rs_malloc` (or game heap allocator behind it) in RecompiledFuncs + free-list head
   symbol (see patches/syms or prior heap_guards). Prefer instrument in fixup_game_funcs.py
   (regen-safe), not hand-edit only.
2. Batch ONE build with counters for the 0x136C path AND a same-run positive control:
   - every `rs_malloc` size (rate-limited) OR specifically size==0x136C + nearby sizes
   - free-list head / free-bytes / failure reason at null return
   - positive control: a known-good malloc that MUST log (e.g. first success after hangar-sel,
     or any malloc size that class-D path already does successfully)
3. Discriminating outcomes on recovery-active class-D (reuse s624 recipe BUDGET≥900):
   - **O1** free-head null / free-bytes < 0x136C at fail → heap pressure / exhaustion
   - **O2** free-head looks healthy + size wrong path → wrong arg / unit mismatch
   - **O3** free-list corruption (head non-null but invalid) → freelist integrity class
   - **O4** positive control silent → instrument miss (not a null result)
4. Do NOT soft-skip thr12 create. Do NOT remove state==5 gate. Do NOT raise HOLD_S past 210.
5. Arm -387 freeroll (do_rom_read+submitDmaSlot+processAssetLoadStep) as 1st free-reroll.
6. Do NOT merge -385 root cause with -387 residual crash.

## Hypotheses (active)

| ID | Claim | Discriminator |
|----|-------|---------------|
| H-ltexmg1 | (CONFIRMED s624) guard LIVE | ltexmg≥1 ∧ ltex_null=0 |
| H-ltexOOM | null malloc = heap pressure | free-head/bytes at fail vs pos ctrl |
| H-ltexArg | null = wrong size/arg | size log ≠ 0x136C or unit scale |
| H-ltexFree | null = freelist corrupt | head invalid / loop |
| H-recovwait1 | (CONFIRMED) recov ~+22s | RECOV_WAIT=50 |
| H-dmarom1 | (1×) post-soft-skip DMA | 2nd same host stack → escalate -387 |
| H-matfree1 | SUPPORTED | 0 more matfree scored |

## Do NOT
- uint32 KSEG0 MEM bases
- Remove state==5 FORCE_STATE6 gate
- Raise HOLD_S past 210
- Soft-skip thr12 without fixing null alloc
- Merge -385 root cause with -387/-384/-373/-386
- Leave FORCE tools default-ON
- Trust thr11d_post without thr11d_new
- Declare null instrument without same-run positive control

### Reference tags
`[level-tex-malloc-guard]`, `ltexmg`, `rs_malloc`, `0x136C`, `0x80048248`,
`loadLevelTextureCache`, `do_rom_read`, `submitDmaSlot`, `processAssetLoadStep`,
`0x800290d4` (STALE), H-ltexOOM, H-recovwait1
