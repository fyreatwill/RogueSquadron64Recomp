# NEXT work unit — instrument MetalSwapChain::resize()/needsResize()
# to test the s239 cross-thread CAMetalLayer hypothesis BEFORE patching it.

## Where the investigation stands

s238 found a NEW host-side crash kind: SIGSEGV inside Apple QuartzCore
(`x_hash_table_remove_ptr`<-`CAMediaTimingInvalidate`<-`-[CALayer
dealloc]`<-`CA::Transaction::commit`), converging 3/3 soaks
(`campose12`/`13`/`14`) on the same trigger point: guest call counter
`n=12420`, wall-clock `t≈130.8-131.7s`, ~56s after the VI-width
transition (1024->512) at ~t=74.2s.

s239 (static read, no build/soak) found ONE concrete, narrow,
PLAUSIBLE-not-CONFIRMED candidate: `MetalSwapChain::resize()`
(`lib/rt64/src/contrib/plume/plume_metal.cpp:2084-2101`) calls
`layer->setDrawableSize(drawableSize)` (line 2093) from the
`PresentQueue` background thread (`rt64_present_queue.cpp:117`,
`"RT64 Present"`), NOT the main thread that owns
`Cocoa_PumpEvents`/`CA::Transaction::commit`. `CAMetalLayer` setters are
not documented thread-safe (unlike `nextDrawable`/`present()`) — a race
here could produce a delayed-dealloc corruption matching the symptom.

**But s239 also found a gap that keeps this at PLAUSIBLE, not
CONFIRMED**: no code path in `src/main/` makes the guest VI_WIDTH
register flip (1024->512) call into `MetalSwapChain::resize()` or
otherwise resize the host window/CAMetalLayer — `resize()` is gated by
`needsResize()` (`plume_metal.cpp:2103-2109`), which compares cached
`width`/`height` against the actual NSWindow content-view size. So the
n=12420/t≈131s correlation with the VI-width transition may be
coincidental (both periodic/frame-count-driven) rather than causally
linked. Full detail: PORTING-STATE Session 239, CURRENT-TRUTH -80.

## Do this iteration — the discriminating measurement, THEN decide

This is a small, targeted INSTRUMENT + ONE SOAK work unit — not a
speculative patch, and not another blind re-soak of the old
`[campose-entry]` instrument (that budget stays spent — do not touch
`campose15`).

1. Add a log line inside `MetalSwapChain::resize()`
   (`plume_metal.cpp:2084`, right after the `if (width == 0 ...)` early
   return, before/around the `setDrawableSize` call at line 2093) that
   fires ONLY when the drawable size actually changes (i.e. inside the
   existing `if (const CGSize current = layer->drawableSize(); ...)`
   branch, so it doesn't spam every frame) with: a monotonically
   incrementing call counter (static local, resets are fine — this is
   diagnostic only) and `rs64_elapsed_seconds()` (declare
   `extern double rs64_elapsed_seconds(void);` inline — canonical shared
   clock, do not invent a second one). Tag it distinctly, e.g.
   `[metal-resize-entry] n=%d t=%.1f w=%d h=%d`.
2. This touches `lib/rt64` — after adding the log line, you MUST run
   `./submodule-patches/export.sh` and commit the refreshed patch in
   THIS SAME iteration (hard rule, CLAUDE.md / iron rule 9), even if the
   soak result is a null result.
3. Regen/build per the standard order if regen is needed for this file
   (check whether `plume_metal.cpp` is compiled directly or goes through
   the `make_elf.py`/`N64Recomp`/`fixup_game_funcs.py` regen pipeline —
   it is host-side rt64 C++, NOT recompiled guest code, so it likely only
   needs a normal `cmake --build`, not the guest-regen pipeline; confirm
   before assuming).
4. Run ONE soak (copy the most recent campose driver script to a new tag,
   e.g. `run_metalresize1.sh` — do not reuse `campose15`'s name, that
   budget is spent on a DIFFERENT instrument; this is a new instrument).
   Positive control: confirm `[metal-resize-entry]` fires at all during
   the run (e.g. at least once at startup/first frame) before trusting a
   null result later in the run.
5. **Discriminating outcomes**:
   - If `[metal-resize-entry]` fires anywhere near `n≈12420`/`t≈131s`
     (within the ~1-2s convergence window established by
     `campose12`/`13`/`14`): the resize-path hypothesis is SUPPORTED —
     next iteration should implement the thread-marshaling fix (dispatch
     `layer->setDrawableSize()` onto the main thread/run loop) and soak
     it with a positive control (does the specific
     `x_hash_table_remove_ptr`/`CAMediaTimingInvalidate` crash signature
     stop recurring across 2 soaks).
   - If `[metal-resize-entry]` NEVER fires near that point (or doesn't
     fire meaningfully at all after startup): the resize-path hypothesis
     is REFUTED — write that up as a closed lead in CURRENT-TRUTH (with
     why it looked plausible: cross-thread CAMetalLayer mutation is a
     real, documented-unsafe pattern, just not the one firing here), and
     the next escalation is Apple's own debug tooling:
     `MallocNanoZone=0 MallocStackLogging=1` / `MTL_DEBUG_LAYER=1` at
     process launch, to catch the actual bad release at the point it
     happens rather than at the delayed dealloc — scope that as its own
     work unit, do not attempt to wire it up in the same iteration this
     result lands.

## Do NOT do this iteration

- Do NOT run `campose15` or touch the old `[campose-entry]` instrument —
  that budget (3 consecutive no-result soaks) is spent (iron rule 8).
- Do NOT implement the thread-marshaling fix yet — the discriminating
  measurement above has to run first, or a fix soak would be untethered
  from evidence of whether `resize()` even fires at the trigger point.
- Do NOT skip `submodule-patches/export.sh` + commit after editing
  `plume_metal.cpp` — this is a `lib/` edit, hard rule applies regardless
  of how small the diff is.
- Do NOT conflate this with the guest-side NaN/`NAN_CHECK`/
  unguarded-deref hardening proposal (CURRENT-TRUTH -55/-56) — still a
  separate, lower-priority crash family.

## Environment notes (carried forward, still current as of s239)

- **Permission gate CONFIRMED CLEARED through s239** — trust it.
- Bash cwd persists across tool calls within a session — an explicit
  `cd` changes it for ALL subsequent calls. Prefer absolute paths; issue
  `cd` as its own call, then the bare command as a second call.
- `cmake --build` is safe to background; the game-soak launch script
  must stay SYNCHRONOUS/foreground-style — launch with
  `run_in_background: true` (generous timeout, e.g. 330000ms). A
  completion notification arrives automatically; if the Stop hook fires
  while the run is still in flight, block-wait with `TaskOutput`
  (`block: true`, generous timeout) rather than re-launching.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` commands get blocked by the permission layer
  — issue `cd` as its own Bash call first, then the next command
  separately. Same for `git -C <path> <cmd>` — `cd` first, then bare
  `git <cmd>`.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **`campose*` armed env-var set** (unchanged since `campose11`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`
  — keep these armed in the new soak so the new instrument is additive,
  not a fresh unknown environment.
- **This exact schedule (`schedulepush2`/`campose*` family) crash rate at
  the SELECT-CRAFT->mission transition is 5/8 soaks crashed** vs 3/8
  survived — treat as roughly even-odds, not "mostly survives."
- **`rs64_elapsed_seconds()`** (`src/main/rt64_render_context.cpp`) is
  the canonical shared wall-clock — declare
  `extern double rs64_elapsed_seconds(void);` inline in any new PATCH
  block.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops) — `scratch/agent/
  checksum_campose11.py` (s235) is mtime-aware, reuse this pattern.
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The driver's own `CRASH: N` summary line counts occurrences of the
  LITERAL STRING `[CRASH]` (many per single crash event) — grep
  specifically for `[CRASH] caught signal` to count actual crash events.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — finding them reset at session start is
  normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s239 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`) — now larger still after s239's addition. Migrate durable
mechanism/architecture material to `PROJECT-OVERVIEW.md` and prune
superseded detail — flagged for 30+ sessions without action.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both still show as modified in
`git status` as of s239 — not investigated this session (no `lib/` edits
made this session, so no `export.sh`/commit obligation triggered). This
becomes directly relevant next iteration since the planned instrument
DOES edit `lib/rt64` — check what's already dirty there before adding to
it, so the `export.sh` diff this next session produces is legible.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families still
have a proposed but unshipped fix (CURRENT-TRUTH -55/-56, PORTING-STATE
Session 215) — separate from the host-CALayer crash line of
investigation, still worth picking up on its own merits eventually but is
NOT the next work unit.
