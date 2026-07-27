# NEXT work unit — M3: root-cause the s86 `queueGPUUploadTMEM` zero-size assert

s86 ran one soak testing the s85 shared-corruption-race hypothesis
(`env ROGUESQ_LOG_DMA=1 PROBE_MODE=start_only HOLD_S=30 zsh
scratch/s73_post_a_scene/run_mission_keys.sh <tag> 0 12`, thread-identity
fields already added to `[rom-read]`, `lib/N64ModernRuntime/librecomp/src/pi.cpp:65-85`).
`do_rom_read` never corrupted this run (488/488 calls sane, all `thr_id=2`,
all in-range/aligned) — the shared-race test is **inconclusive, not
refuted**: no garbage value existed to correlate. Instead the process died
earlier than any prior soak (hold+~15s) to a brand-new crash:

```
Assertion failed: (!decodeTMEM || ((width > 0) && (height > 0))),
function queueGPUUploadTMEM, file rt64_texture_cache.cpp, line 1285.
```
Stack: `queueGPUUploadTMEM` <- `TextureManager::uploadTexture`
(`rt64_rdp_tmem.cpp:52-66`) <- `State::fullSyncFramebufferPairTiles`'s
per-draw-call lambda (`rt64_state.cpp:1329`, `decodeTMEM=true`, i.e. a
real texture upload, not the raw-TMEM path) <- `State::fullSync` <-
`GBI_RDP::fullSync` <- RDP list processing <- `gfx_thread_func`.

## Why this is now the highest-value target

Crash inventory since s83 is up to 7 sites (spline NaN → Metal SIGSEGV /
thr-resume UAF → frameStartReset SIGBUS → do_rom_read corruption →
**this one**), and each session's "dominant blocker" has just been
whichever fires soonest. This one now fires **earliest of all seven**
(hold+~15s vs. do_rom_read's usual longer window), so it is what blocks
every other item on the list (item 2's shared-race retest, item 3's
thr-resume gate positive control, HOLD_S=60 stick test) from even getting
a chance to run further. Fixing/characterizing it is on the critical path
regardless of which hypothesis about the other six turns out right.

## Competing hypotheses

1. **Legitimate degenerate LOADTILE.** The game occasionally issues a
   LOADTILE/texture-decode call with a genuinely zero-width or zero-height
   sample tile (e.g. an off-screen or culled tile the RDP still walks
   through `fullSyncFramebufferPairTiles`). If so, the fix is to skip the
   upload for that tile (treat like the `width<=0||height<=0` case the
   `dumpTexture` guard at `rt64_rdp_tmem.cpp:42-46` already treats as
   invalid) rather than assert.
2. **Corrupted tile-sample fields — part of the same shared-corruption
   family as items 1–2 in CURRENT-TRUTH's next-steps.** `callTile.sampleWidth`/
   `sampleHeight` derive from RDP tile state (line/mask/lrs/lrt/uls/ult) —
   if that state was smashed by the same race behind the OSThread UAF /
   thr-resume `bad=1` / do_rom_read corruption, this would be an 8th
   symptom of one bug, not an 8th independent one.

## Discriminating measurement

1. In `rt64_state.cpp` around line 1329 (the `uploadTexture` call site),
   when `callTile.sampleWidth <= 0 || callTile.sampleHeight <= 0`, log the
   full `LoadTile` fields (`line`, `mask`, `shift`, `uls`, `ult`, `lrs`,
   `lrt` — whatever `LoadTile`/`callTile` exposes) plus the RDP tile index,
   gated on a new env var (e.g. `ROGUESQ_LOG_TMEM_ZERO=1`), **before** the
   assert can fire (same pattern as s85's `[rom-read]`: log first, so a
   crashing call still leaves its inputs in the log).
2. Rebuild, re-run the same `corrgate1`-style soak with the new var set.
3. **Discriminate:**
   - Tile fields look sane/plausible for a legitimately degenerate tile
     (e.g. `lrs<=uls` or `lrt<=ult`, a real "empty rect" pattern) →
     hypothesis 1 supported. Fix: skip the upload (early return before
     `queueGPUUploadTMEM`) instead of asserting; do not silently clamp
     width/height to 1 (that hides a real "why is this tile empty"
     question — prefer an explicit skip + counter over a silent clamp).
   - Tile fields are themselves wild/inconsistent with any real N64 tile
     descriptor (values outside the 10-bit/12-bit ranges those fields
     should hold) → hypothesis 2 supported; treat as another data point
     for the shared-corruption-race file (cross-reference against
     `[thr-resume]`/`[ost-wb]` the same way item 2 below does for
     do_rom_read).

## Do not

- Do not clamp `width`/`height` to a minimum of 1 to silence the assert —
  same reasoning as the do_rom_read asserts: an assert catching a real
  degenerate case should stay loud until root-caused, not be silenced into
  a wrong-but-alive texture upload.
- Do not re-attempt the do_rom_read shared-race correlation (CURRENT-TRUTH
  next-steps item 2) as the primary target this iteration — it cannot even
  be tested until this earlier-firing crash is out of the way (or at least
  understood well enough to know it's unrelated).
- Budget: this is iteration 1 on the TMEM-assert hypothesis. Per
  ITERATION.md rule 8, stop experimenting after 3 consecutive iterations
  with no discriminating result and go BLOCKED or fall back to
  characterizing it as an unexplained one-off.
