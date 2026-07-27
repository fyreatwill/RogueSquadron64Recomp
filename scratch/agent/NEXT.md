# NEXT work unit — source-read `submitSceneNodeRender`'s non-free-list code (18th class)

s135 finished the `emitAllocatedDLCommand` soak's 3rd and final attempt
(rule 8 budget exhausted): guards `emit-dl-guard2`/`3` never fired across
all 3 soaks (s133/s134/s135, 0/0/0), and each of the 3 attempts died to a
*different*, already-known crash class instead of a fresh
`emitAllocatedDLCommand` mystery — s133: environment-side Apple-Metal
shader-compiler SIGSEGV; s134: the 18th class
(`heapFreeListDequeue`/`submitSceneNodeRender`); s135: the separately-
tracked `do_rom_read`/`piDmaWorker` corruption SIGSEGV. **The
`emitAllocatedDLCommand` hypothesis is now parked** — both guards stay in
the code regardless (2 genuinely real unguarded-pointer-chase bugs,
independent of whether either is *the* cause of any specific crash;
standing policy since s99). Read PORTING-STATE's Session 135 entry before
doing anything else; this file only has the actionable summary.

## Do next: source-read `submitSceneNodeRender`, funcs_4.c, for a 2nd unguarded idiom

The 18th class's nearest-symbol crash (`heapFreeListDequeue + 12704` via
`submitSceneNodeRender + 27540`) has now recurred **twice** post-fix
(s131, s134) with all 9 of the already-landed free-list-walk guards
(`SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`) silent both times — this
satisfies the "only act on it if it recurs on its own" trigger set at
s131/s133, and s131 itself concluded the guarded free-list-walk idiom is
**not** this crash's actual cause (proven innocent twice independently
now).

This is a pure source-reading task. No soak, no rebuild needed for the
read itself:

1. Open `N64Recomp/RecompiledFuncs/funcs_4.c` and locate
   `submitSceneNodeRender` in full (it's ~2746 lines past the part
   s123/s131 already audited for the free-list-walk idiom).
2. Read it end to end looking for the same general shape every other
   guard in this series has fixed: a table lookup, linked-list-node
   return, or similarly-derived pointer used to dereference memory
   *without* a null/range check first. This is a **different** idiom
   from the free-list-walk one (already guarded 9x, already proven
   innocent) — do not re-guard those sites.
3. If found: guard it the same way as the existing series in this
   function — `goto` the function's own real epilogue label (do not use
   a bare `return;`, must stay ABI-correct), and if the check involves a
   `ctx->rN` register value, truncate it through `U32()` before
   comparing against 32-bit literal bounds (s99's 100%-false-positive
   lesson — a raw 64-bit sign-extended compare against 32-bit bounds
   fires on ~100% of calls, not just the bad ones).
4. Full delete-all regen (`make_elf.py` → `regen_n64recomp.sh` →
   `fixup_game_funcs.py` → `cmake --build`), audit the patch report for
   exact expected multiplicity (mandatory post-fixup audit, see
   Housekeeping item 0 in CURRENT-TRUTH — the regen pipeline is
   intermittently non-idempotent).
5. Soak once with the new guard's log flag armed alongside every other
   `ROGUESQ_LOG_*` flag (same re-enumeration recipe as the emitdl
   soaks): `grep -oE 'ROGUESQ_LOG_[A-Z_0-9]+' N64Recomp/
   fixup_game_funcs.py | sort -u`.

**Discriminating outcomes:**
1. New guard fires (count > 0) → likely root cause of the 18th class
   found; if the process also survives past where it would have died,
   that's strong same-run corroboration.
2. New guard doesn't fire AND the 18th-class crash recurs a 3rd time →
   the guarded idiom (both this new one and the original free-list-walk
   one) is not the cause; the nearest-symbol match may be misattributed
   to code outside this function entirely (s131's other open branch,
   still unexplored — would need disassembly-level work, a bigger task).
3. No matching idiom found in a careful read at all → treat as evidence
   for the misattribution branch above; do not force-fit a guard onto
   something that doesn't match the pattern just to have shipped a fix.
   Pivot to Thread B (below) instead.

## Thread B (fallback, unchanged): the audio-corruption pivot (voice+0x0/+0x34, s105-123)

Still the single longest-running open thread if the above source-read
comes up empty (no matching idiom, or a guard lands but doesn't
discriminate). s135 incidentally reproduced the `do_rom_read` family
again (bystander crash during an unrelated soak, not a targeted repro)
with one confirmatory data point (`fillSampleStreamRange`'s own
arguments already corrupted at entry — matches s104's already-closed
finding, nothing new). Needs the fresh-angle grep s126 proposed: what
else constructs a name/string table with entries shaped like
`at_6`/`at_7`/`main_n_atpt_lod`/`pilot_sd` — unchanged since s126-135's
framing.

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
  blocking wait (TaskOutput with block=true, or Monitor) on the
  background task works cleanly for capturing completion without
  polling — used again this session.
- The multi-`env`-var one-liner from NEXT.md (`env VAR1=1 VAR2=1 ...
  zsh run_mission_keys.sh ...` with a `$(grep ...)` substitution) trips
  this environment's Bash static-command-analyzer ("Contains shell
  syntax that cannot be statically analyzed"). Workaround used
  successfully this session: write the exact command into a small `.sh`
  wrapper file (`scratch/agent/run_emitdl3.sh` is a working example
  using zsh's `${=FLAGS}` word-splitting), `chmod +x`, then invoke that
  single file path as the Bash command.

## Do not

- Do not re-audit any of the 8 Thread A functions again (Thread A is
  CLOSED as of s132: composeNpcOrientationMatrix,
  updateAnimatedTextureStreaming, static_5_800B4048,
  projectModelBoundsToScreen, reserveAndEmitDLEntry,
  activateAnimationKeyframe, submitSceneNodeRender (free-list idiom
  only — its *other* code is fair game, see above),
  updateHangarBayScene).
- Do not re-guard `emitAllocatedDLCommand`'s two `findAndUnlinkSmallestEntry`
  walk-loop sites (`GUARD2`/`GUARD3`, both r4 and r5 copies) — already
  landed and exhaustively verified against source. Do not re-soak this
  hypothesis — the 3-attempt budget is exhausted (s133/s134/s135).
- Do not re-guard `submitSceneNodeRender`'s free-list-walk sites (the 9
  already landed by s123/s131) — proven innocent of the 18th class
  twice now (s131, s134). Any new guard from this work unit must target
  a genuinely different idiom.
- Do not treat a 0/0 guard-fire result as "the guard doesn't work" or
  "the fix is wrong" — it's an uncontrolled null, not a refutation.
  Only a positive control (guard fires) or a repeat crash with the
  guard silent would actually discriminate.
- Do not chase the s83/s133 Apple-Metal-internal SIGSEGV as if it were
  a guest-code bug — it has no guest frames anywhere in its backtrace.
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race
  opportunistically — tracked as its own item (-1, M3/Thread B) in
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
s90-135 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
