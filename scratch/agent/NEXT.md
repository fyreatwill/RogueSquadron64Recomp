# NEXT work unit — re-attempt the `emitAllocatedDLCommand` soak (attempt 3/3, FINAL)

s133 guarded the `emitAllocatedDLCommand` crash s132 found (same
`findAndUnlinkSmallestEntry`-return + walk-loop idiom already fixed
elsewhere, inlined here twice — `r4`/`r5` copies, guarded as
`ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`). Two soaks since (s133, s134)
both got a **null result without a positive control** — the guards
never fired (0/0 both times) — but neither died to a fresh mystery:
s133 died to the environment-side Apple-Metal shader-compiler SIGSEGV
(no guest code, not fixable here); s134 died to a **2nd fully-post-fix
recurrence** of the already-catalogued 18th class (`heapFreeListDequeue
+ 12704` ← `submitSceneNodeRender + 27540`, byte-identical to s131's
own backtrace). Read PORTING-STATE's Session 134 entry before doing
anything else; this file only has the actionable summary.

## Do next: re-run the same soak ONE more time (attempt 3/3, per rule 8 — this is the last allowed attempt)

```
cd scratch/s73_post_a_scene
env PROBE_MODE=start_only HOLD_S=30 \
  $(grep -oE 'ROGUESQ_LOG_[A-Z_0-9]+' \
      /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py \
    | sort -u | sed 's/$/=1/' | tr '\n' ' ') \
  ROGUESQ_LOG_THREAD_RESUME=1 \
  zsh run_mission_keys.sh emitdl3 5 12
```

(Re-enumerate the flag list fresh via the grep above — s134 found one
more flag than s133's hardcoded list already, and a future session may
add more. No rebuild needed — the s133 binary is current, unless you've
changed `fixup_game_funcs.py` since s134, which you haven't.)

**Discriminating outcomes** (unchanged from s133/s134's framing):
1. `[emit-dl-guard2]` or `[emit-dl-guard3]` fires (any count > 0) →
   positive control obtained, the s133 fix is confirmed to guard a
   code path that actually executes with a corrupted pointer.
2. The process dies again to a **new** `emitAllocatedDLCommand` SIGBUS
   with the guards NOT firing → the idiom s133 guarded is not what
   this crash actually hits; re-read `funcs_3.c:2412-2948` for anything
   besides the two `findAndUnlinkSmallestEntry`-derived walk loops.
3. A 3rd, different crash preempts again (new OR a recurrence of an
   already-known class, as both s133 and s134 got) → **this exhausts
   the 3-attempt budget.** STOP re-soaking this specific hypothesis.
   Park it (both `emitAllocatedDLCommand` guards stay regardless — they
   fix 2 genuinely real unguarded-pointer-chase bugs independent of
   whether they're THE cause of any specific crash, standing policy
   since s99). Then pick ONE of:
   - **(preferred)** The 18th class (`heapFreeListDequeue` nearest-
     symbol via `submitSceneNodeRender`) has now recurred **twice**
     post-fix (s131, s134), both times with the guarded free-list-walk
     idiom fully silent — satisfying the "only act on it if it recurs
     on its own" trigger set at s131/s133. Source-read
     `submitSceneNodeRender`'s remaining ~2746 lines (`funcs_4.c`) for
     a 2nd, distinct unguarded pointer-chase idiom (not the free-list
     one — that's proven innocent twice now). This is the same
     "2nd-unguarded-site-in-an-already-guarded-function" pattern Thread
     A found repeatedly (s126-132), just not yet applied to this
     specific function's *non*-free-list code.
   - Thread B (fallback, see below): the audio-corruption pivot.

## Do NOT re-open Thread A

Thread A (the systematic re-audit of all 8 multi-hit hangar-tick
functions for a second unguarded deref past their first guard) is
CLOSED as of s132 — final tally 6 hits, 2 clean, of 8 audited:
composeNpcOrientationMatrix, updateAnimatedTextureStreaming,
static_5_800B4048, projectModelBoundsToScreen, reserveAndEmitDLEntry,
activateAnimationKeyframe, submitSceneNodeRender, updateHangarBayScene.
Do not re-audit any of these 8 again. (The "source-read
submitSceneNodeRender's non-free-list code" option above is NOT a
Thread-A re-audit in the closed sense — Thread A audited each
function's *already-known* guarded idiom for a 2nd occurrence; this
would be hunting for an *entirely different* idiom class in the same
function, prompted by a crash recurrence, same as how `emitAllocatedDLCommand`
itself was found via a crash backtrace rather than a list re-audit.)

## Also open, lower priority

- **The 18th class (`heapFreeListDequeue`)** — see above; now recurred
  twice post-fix (s131, s134). Do not chase with a *dedicated* repro
  soak beyond what's already happened; if the emitdl3 attempt above
  also lands on it a 3rd time, that's even stronger grounds to act (see
  above).
- **The s83 Apple-Metal-internal shader-compiler SIGSEGV** — recurred
  a 2nd time in s133 (`fscache_insert_and_retain`), confirmed
  environment-side (no guest code in the backtrace, no source on our
  side). Not fixable by this project's own code; not worth chasing
  further unless it becomes the *dominant* cause of soak deaths (it
  isn't — one occurrence each in s83 and s133, out of dozens of soaks).

## Thread B (fallback, unchanged): the audio-corruption pivot (voice+0x0/+0x34, s105-123)

Still the single longest-running open thread if the `emitAllocatedDLCommand`
lead is parked (attempt 3/3 also fails to discriminate) AND you don't
take the 18th-class source-read option above. Needs the fresh-angle
grep s126 proposed (what else constructs a name/string table with
entries shaped like `at_6`/`at_7`/`main_n_atpt_lod`/`pilot_sd`) —
unchanged since s126-134's framing.

## This session's environment notes (carry forward, still current)

- The guard-placement bug caught s133: when adapting a prior session's
  regex-replacement pattern to a new site, do NOT assume the
  captured-group-plus-append shape (`m.group(1) + guard_code`, check
  happens *after* the deref) is universal — some prior patches use that
  shape deliberately, others (s123/s131's actual free-list guards)
  place the check *before* the deref with no capture group at all.
  Re-derive the correct shape from the specific prior guard you're
  actually modeling, by reading its landed, regenerated output in the
  `.c` file directly — not from whichever nearby Python function you
  copy-pasted last.
- Host-code crash-offset arithmetic (`function + N bytes`) does NOT
  map linearly to guest instruction addresses or source line numbers —
  it's a byte offset into the *compiled host machine code* of that C
  function. Use it only to identify which function/frame crashed, then
  find the matching idiom by reading the function's full source body.
- `rm` on paths outside `scratch/` requires approval and does NOT
  accept glob patterns — list every `funcs_*.c` path explicitly, or
  delete via a `python3 -c` one-liner using `pathlib.Path.glob()`.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same
  session (non-idempotent, s102) — verify patch multiplicity via the
  printed patch report and/or direct `grep -c` on the regenerated `.c`
  files instead.
- `git -C <path> <cmd>` and `cd <path> && git <cmd>` both fail this
  environment's permission prefix-match (rule 10's family) even when
  the underlying `git <cmd>` is allowlisted — issue a bare `cd <path>`
  as its own Bash call first (cwd persists across calls), then the
  plain `git <cmd>` as a second call.
- A `run_mission_keys.sh` soak with `run_in_background: true` and a
  Monitor/Bash-blocking-wait on the child PID works cleanly for
  capturing completion without polling — used this session
  (`kill -0 <pid>` in a loop inside a single blocking Bash call with a
  long timeout, or a Monitor with the same check).

## Do not

- Do not re-audit any of the 8 Thread A functions again.
- Do not re-guard `emitAllocatedDLCommand`'s two `findAndUnlinkSmallestEntry`
  walk-loop sites (`GUARD2`/`GUARD3`, both r4 and r5 copies) — already
  landed and exhaustively verified against source.
- Do not treat s133/s134's 0/0 guard-fire result as "the guard doesn't
  work" or "the fix is wrong" — it's an uncontrolled null, not a
  refutation. Only a positive control (guard fires) or a repeat crash
  with the guard silent would actually discriminate.
- Do not chase the s83/s133 Apple-Metal-internal SIGSEGV as if it were
  a guest-code bug — it has no guest frames anywhere in its backtrace.
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race
  opportunistically — tracked as its own item (-1, M3) in
  CURRENT-TRUTH's next-steps list, separate from this thread.
- When landing any new guard, always truncate a `ctx->rN` value through
  `U32()` before comparing against 32-bit literal bounds (s99's
  100%-false-positive lesson).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2200+ lines,
growing). Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment — not on its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-134 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
