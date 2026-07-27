# NEXT work unit — M3: instrument the 14th crash class (`reserveAndEmitDLEntry`)

s97 spent the last of the 3 allowed identical DMA-caller-repro
attempts (s95/s96/s97, all inconclusive — each died early to a
*different* crash before the ~140s DMA window) and, per rule 8,
pivoted to instrumenting the most-recurring hangar-tick crash class
(`composeNpcOrientationMatrix`, 12th). That instrument got a clean
positive control (597/597 fires, no crash on that path) but the
process died anyway to a brand-new 15th crash class. Read
PORTING-STATE.md's Session 97 entry before doing anything else; this
file only has the actionable summary.

## What's established (do not re-derive)

- The blind DMA-caller repro (`ROGUESQ_LOG_DMA_CALLER=1` +
  `PROBE_MODE=start_only HOLD_S=30`) is **parked** — 3/3 attempts
  spent (s95, s96, s97), each died early to a different unrelated
  crash (12th, 13th, 14th classes respectively), never reaching the
  ~140s window where the indirect-caller phenomenon fires. **Do not
  re-run this exact repro again** as a dedicated work unit. The
  instrument itself stays armed in every soak (it's free) — if it
  ever fires opportunistically during a soak run for a different
  reason, read the backtrace immediately.
- `get_function` (`lib/N64ModernRuntime/librecomp/src/overlays.cpp:397`)
  is the confirmed chokepoint for every indirect call (s95); the
  known boot-time `submitDmaRequestBatch` call is direct and
  structurally cannot trigger the instrument. **Do not re-derive
  this.**
- Do NOT re-plan "dump the `OSIoMesg` at `mb`" (refuted s92) or cite
  `ra=0` as corruption evidence (refuted s92, routine on 487+ calls,
  reconfirmed s97 on `composeNpcOrientationMatrix`'s own log).
  Do NOT re-open "index-desync consumer bug" or "external RDRAM
  stomp" — s94's producer-side log already shows corruption at
  write-time, ruling out both.
- Do NOT re-grep for `submitDmaRequestBatch(rdram` or the
  `LOOKUP_FUNC(` call-site count — both done, stable, not changing.
- `ROGUESQ_LOG_COMPOSE_NPC=1` (12th class, `static_5_800AB1C8`) is
  landed, correctly implemented, and confirmed working (597/597
  fires in one soak). Its own SIGBUS did NOT recur in that soak — now
  2-for-5 across sessions that reached the hangar-tick window (hit
  s74, s95; clean s92, s93, s97). Not strong enough to retire the
  class; also not urgent to re-test in isolation (see "The work
  unit" below for why something else ranks higher).
- Do NOT re-check whether any of the `ROGUESQ_LOG_*` instruments add
  meaningful overhead — checked and refuted for `DMA_CALLER` at the
  source (s96); the same reasoning (single int compare + cached
  `getenv`) applies to every instrument in this family, they all
  follow the identical pattern.

## The crash-class picture (15 total, all in `M3`)

Two families:
- **Hangar-tick / `MEM_W`-off-an-arg family** (guest-side code, real
  bugs, fixable): 9th `updateAnimatedTextureStreaming` (1x, s89),
  10th `static_5_800B4048` (1x, s90), 11th `projectModelBoundsToScreen`
  (1x, s92), 12th `composeNpcOrientationMatrix` (2x: s74, s95),
  **14th `reserveAndEmitDLEntry`** (1x, s97, **not yet instrumented —
  this session's target**).
- **RT64-internal asserts** (no source-level bug on our side, same
  class as the s86 TMEM-zero assert): 13th `reinterpretTileRecord`
  (1x, s96), 15th `loadDrawState` zero-sample-size (1x, s97). Not
  useful to instrument (no fix available even once characterized);
  only worth tracking recurrence counts.

Every soak that has reached the "SELECT YOUR CRAFT stable → hold"
window in the last 3 sessions (s95, s96, s97 x2) has died to a
**different, previously-unseen** crash. That pattern — not any single
crash class — is now the dominant obstacle to reaching the ~140s DMA
window at all.

## The work unit

Instrument the 14th class (`reserveAndEmitDLEntry`) — guest-side,
fixable, and reducing the crash-class roulette is the direct lever on
"soaks keep dying before reaching their target window." RT64-internal
classes (13th, 15th) are not worth instrumenting since there is no
fix to reach for even after characterizing them.

1. Find `reserveAndEmitDLEntry` in `N64Recomp/RecompiledFuncs/*.c`
   (`grep -rn "RECOMP_FUNC void reserveAndEmitDLEntry" RecompiledFuncs/`
   from `/Users/williambuckley/Documents/Tools/N64Recomp`). Read its
   prologue (first few lines after the standard `hi/lo/result/c1cs`
   init) to find the right insertion point — follow the exact pattern
   used for `_hangar_entry_patch`/`_compose_npc_orientation_patch` in
   `fixup_game_funcs.py` (search those two function names for the
   template).
2. Add a new patch block: `ROGUESQ_LOG_DLENTRY=1` (or similar name),
   logging `ctx->r4`/`ctx->r5`/`ctx->r31` (a0/a1/ra) at entry, in
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
3. `cd /Users/williambuckley/Documents/Tools/N64Recomp && python3 fixup_game_funcs.py`
   — verify it reports `patched x1` for the new function, not x0 (x0
   means the prologue regex didn't match — re-check by reading the
   actual generated prologue text, don't guess).
4. Rebuild: `cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j 8` — must be exit clean, no new errors (pre-existing `-Wformat` warnings on `%08X` vs `gpr`/`uint64_t` in sibling instruments are known-benign, not yours to fix).
5. Soak with the full flag set (add the new flag; keep everything
   else, `ROGUESQ_LOG_THREAD_RESUME=0` mandatory per the s93 confound
   fix):
   ```
   env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
       ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
       ROGUESQ_LOG_COMPOSE_NPC=1 ROGUESQ_LOG_DLENTRY=1 \
       ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_RING=1 ROGUESQ_LOG_DMA_CALLER=1 \
       ROGUESQ_LOG_THREAD_RESUME=0 \
       PROBE_MODE=start_only HOLD_S=30 zsh \
       scratch/s73_post_a_scene/run_mission_keys.sh s98_dlentry1 0 12
   ```
   (rename the flag in this command to whatever you actually landed
   in step 2, and update this doc to match if it changes.)

Outcomes:

1. **Instrument fires with a crash on `reserveAndEmitDLEntry`
   recurring** — read the logged args; likely another
   unchecked-pointer-deref shape, same family as 9th–12th. If the
   value looks like a plausible-but-wrong pointer (not obviously
   garbage), that's worth a source read of the function itself for
   the actual dereference site.
2. **Instrument fires cleanly (positive control) but a DIFFERENT,
   newer crash preempts it (16th class)** — same escalating pattern
   as s97. If this happens, STOP adding one-off instruments for new
   crashes and treat "this window has an unusually high crash
   density" as the finding itself; consider whether a *shorter* hold
   or a narrower probe schedule could reach the DMA-caller window
   before hitting any of this family (i.e. attack the timing, not the
   individual crashes).
3. **Soak reaches ~140s / the DMA window without dying** — genuinely
   new territory; re-check `ROGUESQ_LOG_DMA_CALLER` and
   `do_rom_read` per the original M3 question (item 1 in
   CURRENT-TRUTH's Next Steps).

## Do not

- Do not re-run the plain DMA-caller repro as a dedicated work unit
  (parked, 3/3 spent, s97).
- Do not re-grep for `submitDmaRequestBatch(rdram`, ring literal
  constants, or `LOOKUP_FUNC(` call-site counts — all done, stable.
- Do not cite `ra=0x00000000` as corruption evidence — routine
  (s92, reconfirmed s97).
- Do not re-plan "dump the `OSIoMesg` at `mb`" — refuted (s92).
- Do not re-open "consumer index-desync" or "external stomp after a
  clean write" — s94 rules out both.
- Do not combine `ROGUESQ_LOG_THREAD_RESUME=1` with any of these
  repros without a specific reason — confirmed confound (s93).
- Do not spend a soak trying to characterize the 13th or 15th crash
  classes (RT64-internal asserts, no fix available on our side) —
  only worth noting if they recur.
- Do not grep `run.log` for the script's own `[keys]`/phase-timing
  lines — they're in the Bash tool's own stdout capture, not
  `run.log` (s96).
