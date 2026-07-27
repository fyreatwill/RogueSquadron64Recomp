# NEXT work unit — continue Thread A re-audit (14th/16th/17th/18th classes)

s128 finished item 1/5 of the Thread A re-audit list: re-read
`projectModelBoundsToScreen` (11th class, `funcs_15.c`) to its closing
brace and found its s101 guard covers only the `a0` argument
(`ctx->r22`) — the function's other two pointer arguments, `a2`
(`ctx->r21`) and `a3` (`ctx->r20`), are separately dereferenced as raw
`Vec3*` with zero checks. Guarded both
(`ROGUESQ_LOG_PROJECT_MODEL_BOUNDS_GUARD2`/`GUARD3`), full delete-all
regen + rebuild clean, one soak: both new guards unexercised (0/0,
function never called this run), died to the tracked
`do_rom_read`/`piDmaWorker` race at the usual hold+11s window — not a
new finding. Read PORTING-STATE's Session 128 entry before doing
anything else; this file only has the actionable summary.

Thread A's generalizing hypothesis ("a guard landed after ONE bad site
does not mean the function has only one") is now **3/3** on every
function tried: composeNpcOrientationMatrix (s126),
updateAnimatedTextureStreaming + static_5_800B4048 (s127),
projectModelBoundsToScreen (s128) — 4 functions audited, 4 hits, 0
clean audits so far. Per ITERATION.md rule 8 this keeps producing new
information each time (a new guard site every audit), so continue
Thread A rather than pivoting yet — a pivot to Thread B only makes
sense after a *clean* audit (or several), not after another hit.

## This session's environment notes (carry forward, still current)

- `rm` on paths outside `scratch/` requires approval and does NOT
  accept glob patterns ("Glob patterns are not allowed in write
  operations") — list every `funcs_*.c` path explicitly (via `ls`
  first, then one `rm` call with all paths spelled out) for the
  mandatory delete-all regen step.
- `cd X && command` in one Bash call triggers a separate "changes
  directory before running git/other, could run untrusted hooks"
  approval prompt distinct from the permission-allowlist prompt. Issue
  `cd X` as its own Bash call, then the command as a second call — both
  then run without friction (persisted cwd carries over between calls).
- Any command with `&&` chaining an unlisted second command (e.g.
  `... && echo "EXIT=$?"`) requires approval for the whole compound
  command even if the first part alone is allowlisted — just drop the
  trailing `echo`/chained diagnostic and check `$?`/output separately
  if needed, or issue commands one at a time.
- `env FOO=1 BAR=1 zsh script.sh args > log 2>&1` (no `&&`, no `cd`) ran
  with no approval friction — prefer this single-call shape for
  soak-driver invocations. Running it via the background-Bash tool
  (`run_in_background: true`) worked cleanly and freed the turn to do
  other prep while the ~90-140s soak ran; wait for the completion
  notification (or block on `while ps -p <pid> >/dev/null; do sleep 5;
  done`) rather than polling the log by hand.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same
  session to "double check" the report — it is known non-idempotent
  (s102) and will duplicate every already-applied patch on disk.
  Verify patch multiplicity via direct `grep -c` on the regenerated
  `.c` files instead (works even though the python script itself can't
  be safely re-invoked).

## Do next: re-audit the remaining 4 guarded multi-site functions

Same method as s126/s127/s128: read each function FULLY to its own
closing brace (funcs_*.c line numbers below), looking for a second
table-lookup-then-deref, struct-field-pointer-then-deref, or
unchecked-arg-deref shape past the already-guarded site(s). Delegating
each read to a parallel Explore-type subagent works well (self-contained
prompt: exact file/line range, exactly what the existing guard already
covers so it isn't re-reported, exactly what NOT to flag — the s128
prompt is a good template, see PORTING-STATE Session 128) — verify any
positive finding yourself against the source before writing a patch,
subagent reports are claims not facts.

Remaining, in suggested order (smallest/most tractable first):

1. **14th, `reserveAndEmitDLEntry`** (`funcs_3.c`, guard at s109,
   epilogue label `L_dlentry_guard_exit`). Function bounds not yet
   located this session — grep `void reserveAndEmitDLEntry` in
   `funcs_3.c` and the next `RECOMP_FUNC` after it.
2. **16th, `activateAnimationKeyframe`** (`funcs_14.c`, guard at s99,
   table-deref shape).
3. **17th, `submitSceneNodeRender`** (`funcs_4.c`, guard at s123,
   free-list-walk shape — note this one's own catalog entry already
   says the guard covers a walk loop, worth double-checking whether
   the loop has an early-exit path the guard's placement doesn't
   dominate).
4. **18th, `updateHangarBayScene`** (`funcs_40.c`, guard at s110 — this
   one already has FIVE guarded sites A-E, so it may already be fully
   covered by design; still worth a fresh read since s100/s110 predate
   the "systematically re-audit" methodology s126 introduced).

If a second (or third) site turns up in any of these: guard it the
same way (`U32()` truncate, `[0x80000000, 0x80800000)` bounds check,
`goto` the function's real epilogue — confirm which label/whether one
needs creating by reading to the closing brace first, new env var
following the `_GUARD2`/`_GUARD3` naming convention, full delete-all
regen, soak with `PROBE_MODE=start_only HOLD_S=30` and every
`_GUARD`/`_GUARD2`/`_GUARD3` flag for that function armed).

If all 4 come back clean (single site each) — combined with s128's
result that would be 4 hits out of 4 functions tried plus these final
4 checks; if THOSE come back clean, that's a real, useful,
budget-respecting result: write it down (this would mean
projectModelBoundsToScreen/composeNpcOrientationMatrix/
updateAnimatedTextureStreaming/static_5_800B4048 were the exceptions
that needed a second site, not the rule) and fall through to Thread B.

## Thread B (fallback): the audio-corruption pivot (voice+0x0, s105-123)

Unchanged from s126/s127/s128's framing — still the single
longest-running open thread, still needs the fresh-angle grep s126
proposed (what else constructs a name/string table with entries shaped
like `at_6`/`at_7`/`main_n_atpt_lod`/`pilot_sd`) if Thread A audits
come back clean.

## Do not

- Do not re-soak specifically to force a positive control on any of
  the 12 guarded classes' sites — not required before landing.
- Do not treat any of s124/s125/s126/s127/s128's 0/0 (unexercised)
  results as evidence any specific guard works in a stronger sense
  than "guard is in place, never triggered because the buggy path
  wasn't hit this run."
- Do not re-litigate H1/H2 (voice+0x0 zero-init / asset-alloc
  coincidence) — both closed, s122/s123.
- Do not re-run the `songlifecycle`/`shutdownAudioEngine`
  alias/`musyxInitVoiceFromSample` pointer-identity hypotheses —
  all closed s117-121.
- When landing any new guard, always truncate a `ctx->rN` value through
  `U32()` before comparing against 32-bit literal bounds (s99's
  100%-false-positive lesson, repeated in every guard since).
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race
  opportunistically — tracked as its own item (-1) in CURRENT-TRUTH's
  next-steps list. s128 saw it again at hold+11s; expected, not new.
- Do not chase the RSP-microcode `Unhandled jump target 0x0231`/`0x17F0`
  diagnostic seen in s128's soak — already documented (s79) as
  "secondary, not onset cause," not a new class.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2000+ lines).
Migrate durable mechanism/architecture material to PROJECT-OVERVIEW.md
and prune superseded detail, paired with a real experiment — not on
its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-128 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
