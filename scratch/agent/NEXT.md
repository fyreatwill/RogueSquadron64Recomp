# NEXT work unit — pin down the 18th crash class's real fault site (s123)

s122 source-refuted literal H1 for the `voice+0x0` mystery
(`allocateSongChannelArray` already zero-inits every live voice's byte 0
right after `rs_malloc`, unconditionally — see PORTING-STATE Session 122)
and landed `ROGUESQ_LOG_ASSET_ALLOC=1` to test H2's address-coincidence
question, but got 0/2 same-run corruption positive controls (the
`[voice-active-gate-nz]` instrument never fired in either soak) — so
that specific test remains **untested**, not refuted. Read PORTING-STATE's
Session 122 entry before doing anything else; this file only has the
actionable summary.

The 2nd `assetalloc` soak died to a **2nd occurrence of the already-
catalogued 18th crash class** (first seen s108, `docs/CURRENT-TRUTH.md`
"M3" section, nearest-symbol `heapFreeListDequeue + 12704` via
`submitSceneNodeRender` ← `processSceneNode` ← `traverseSceneGraphRecursive`
← `setupCameraMatrices`). Per this codebase's own established convention
(every other class in the hangar-tick-crash family — 12th, 16th, 17th —
got source-read + guarded on its 2nd recurrence), this is now the
highest-information-value next step: a confirmed-recurring, uninstrumented
crash beats a 3rd blind attempt at a co-occurrence that's been null twice.

## Why this beats a 3rd asset-alloc soak

Rule 8 (3 consecutive same-hypothesis attempts with no discriminating
result → stop and reassess) isn't triggered yet (2/3 used), but the
asset-alloc/voice-gate co-occurrence soaks aren't just non-discriminating
— they're not even reaching the condition being tested (0/2
`[voice-active-gate-nz]` fires at all). A 3rd attempt with the same soak
shape has no reason to behave differently. The 18th-class crash, by
contrast, just went from "1 occurrence, not chased" to "2 occurrences,
same family's own trigger condition met" — a genuinely new, actionable
data point, not a repeat of the same null.

## The work unit

1. **Source-read first** (do not instrument blind). Find
   `submitSceneNodeRender` in the recompiled tree (`grep -rn
   "submitSceneNodeRender" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c`
   — it will show up as a `RECOMP_FUNC` definition in exactly one file
   and as call-site comments elsewhere) and read the function body.
   Remember: this family's crash sites have consistently turned out to
   be an unguarded table-lookup-then-dereference (12th, 16th class) or
   an unguarded arg-pointer deref (11th, 14th class) — check for that
   shape first, matching the `_composeNpcOrientationMatrix`/
   `_activateAnimationKeyframe`/`_projectModelBoundsToScreen` template
   already in `fixup_game_funcs.py` (search for those names to see the
   guard pattern: entry diagnostic + `goto` to the function's own real
   epilogue label, `U32()`-truncated bounds check — s99's own postmortem
   flags the truncation step as mandatory, a bare 64-bit `ctx->rN`
   compare against 32-bit bounds is a documented false-positive trap).
2. **Do not trust "nearest exported symbol" as the actual crash site.**
   `heapFreeListDequeue + 12704` is known-imprecise for this family
   (large per-frame offsets are normal here, not a symbolication bug) —
   the real fault could be many instructions past that export, possibly
   in a different (static/inlined) function entirely. If `nm`/symbol
   lookup on the built binary can narrow the offset further, do that
   before guessing which recompiled C function actually contains
   guest address implied by the offset.
3. **If a clear unguarded-deref shape is found**, land a guard following
   the exact template already used 3 times in this file (entry log +
   `goto` real-epilogue + `U32()`-safe bounds check), full delete-all
   regen, audit the patch report for `x1`, rebuild, one soak to check
   for a clean negative control (this function's own guard doesn't fire
   0/N is fine, that's expected — positive control on the crash itself
   recurring is the harder bar, don't require it before landing the
   guard, precedent: s99-s110 all landed guards without a same-session
   positive control).
4. **If no clear deref shape is found** (this class might be genuinely
   inside `heapFreeListDequeue` itself, i.e. real heap/allocator
   corruption rather than a guest-code bug), do not force a guard —
   report it as RT64/allocator-internal (like the 13th/15th/19th classes)
   and move to the next item below instead.

## Opportunistic, no extra cost

Keep `ROGUESQ_LOG_ASSET_ALLOC=1` and `ROGUESQ_LOG_VOICE_ACTIVE_GATE=1`
armed in whatever soak this work unit runs (both already landed, free to
leave on) — if `[voice-active-gate-nz]` happens to fire this time, that's
a 3rd, free data point for the H2 coincidence question without spending
a dedicated soak on it.

## Do not

- Do not re-run the `songlifecycle` idx-vs-count soak shape — closed,
  3/3 attempts, s121 gave a clean discriminating result (PORTING-STATE
  s121).
- Do not re-test the `shutdownAudioEngine` alias hypothesis as causal —
  refuted 2/2 (s120).
- Do not re-litigate hypothesis (b) (`musyxInitVoiceFromSample`
  comparison) — closed s117-119.
- Do not treat s122's `caller_ra=0x00000000` (all 6 `[asset-alloc]`
  fires, both soaks) as a corruption signal — s92 already established
  this is routine (thread-dispatch-context artifact), seen identically
  in 3 unrelated entry logs.
- When landing a new guard, always truncate a `ctx->rN` value through
  `U32()` before comparing against 32-bit literal bounds — s99's own
  guard had a 100%-false-positive bug from skipping this.

## Regen reminder (delete-first is mandatory; audit every run)

1. Delete all existing output first (do NOT skip this):
   ```
   python3 -c "
   from pathlib import Path
   import os
   base = Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs')
   for f in base.glob('funcs_*.c'): os.remove(f)
   "
   ```
2. `python3 <rogue_squadron64>/tools/make_elf.py` (absolute path, no `cd`)
3. `zsh tools/agent/regen_n64recomp.sh` (wraps
   `cd .../N64Recomp && ./build/N64Recomp rogue_squadron.toml` as a
   single allowlisted command)
4. `python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   — read the full report, not just grep for your own patch — confirm
   every line's `x{n}` matches its expected/intentional multiplicity
   (audio gate `x3`, musyxKeyOnVoice div-traps `x8`, everything else `x1`).
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   — grep for `error:` explicitly.
6. Soak via `env <FLAGS> PROBE_MODE=start_only HOLD_S=30 zsh
   scratch/s73_post_a_scene/run_mission_keys.sh <tag> 5 8`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is over the ~35 KB target. Migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-122 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
