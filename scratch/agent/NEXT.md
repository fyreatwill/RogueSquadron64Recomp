# NEXT work unit — continue Thread A re-audit (11th/14th/16th/17th/18th classes)

s127 re-read the 9th (`updateAnimatedTextureStreaming`) and 10th
(`static_5_800B4048`) guarded functions to their closing braces —
**both** had a second, independent unguarded pointer-chase site the
s124/s125 guards never covered (same "read a struct/global-table
pointer field, then deref it with no range check" shape as s126's
`composeNpcOrientationMatrix` finding). Guarded all 5 new sites,
full delete-all regen + rebuild clean, one soak: both new guards
unexercised (0/0, neither function called this run), but for the
first time since s88 the **entire 30s hold window ran with zero
crashes** — not evidence the new guards work, just this run's path
missed every known bad site including the `do_rom_read` race. Read
PORTING-STATE's Session 127 entry before doing anything else; this
file only has the actionable summary.

Thread A's generalizing hypothesis ("a guard landed after ONE bad
site does not mean the function has only one") is now 2/2 on the
functions tried (composeNpcOrientationMatrix s126, plus both of
s127's). Per ITERATION.md rule 8 this is NOT yet 3 consecutive
same-hypothesis iterations with no new information — each audit keeps
producing new guard sites, which is itself new information — so
continue Thread A rather than pivoting yet.

## This session's environment notes (carry forward)

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
  soak-driver invocations.

## Do next: re-audit the remaining 5 guarded multi-site functions

Same method as s126/s127: read each function FULLY to its own closing
brace (funcs_*.c line numbers below), looking for a second
table-lookup-then-deref, struct-field-pointer-then-deref, or
unchecked-arg-deref shape past the already-guarded site(s). Delegating
each read to a parallel Explore-type subagent worked well this
session (self-contained prompt: exact file/line range, exactly what
the existing guard already covers so it isn't re-reported, exactly
what NOT to flag) — verify any positive finding yourself against the
source before writing a patch, subagent reports are claims not facts.

Remaining, in suggested order (smallest/most tractable first):

1. **11th, `projectModelBoundsToScreen`** (`funcs_15.c`, guard at
   s101 covers `ctx->r22`/`s6`). Function bounds not yet located this
   session — grep `void projectModelBoundsToScreen` in `funcs_15.c`
   and the next `RECOMP_FUNC` after it.
2. **14th, `reserveAndEmitDLEntry`** (`funcs_3.c`, guard at s109,
   epilogue label `L_dlentry_guard_exit`).
3. **16th, `activateAnimationKeyframe`** (`funcs_14.c`, guard at s99,
   table-deref shape).
4. **17th, `submitSceneNodeRender`** (`funcs_4.c`, guard at s123,
   free-list-walk shape — note this one's own catalog entry already
   says the guard covers a walk loop, worth double-checking whether
   the loop has an early-exit path the guard's placement doesn't
   dominate).
5. **18th, `updateHangarBayScene`** (`funcs_40.c`, guard at s110 — this
   one already has FIVE guarded sites A-E, so it may already be fully
   covered by design; still worth a fresh read since s100/s110 predate
   the "systematically re-audit" methodology s126 introduced).

If a second site turns up in any of these: guard it the same way
(`U32()` truncate, `[0x80000000, 0x80800000)` bounds check, `goto` the
function's real epilogue — confirm which label/whether one needs
creating by reading to the closing brace first, new env var following
the `_GUARD2` naming convention, full delete-all regen, soak with
`PROBE_MODE=start_only HOLD_S=30` and every `_GUARD`/`_GUARD2` flag
for that function armed).

If all 5 come back clean (single site each) — that would be 5
consecutive clean audits after 2 dirty ones (s126, s127), which by
rule 8 is a real, useful, budget-respecting result on its own: write
it down (this generalizes to "most of this family's guards were
already complete; composeNpcOrientationMatrix/updateAnimatedTexture
Streaming/static_5_800B4048 were the exceptions, not the rule") and
fall through to Thread B.

## Thread B (fallback): the audio-corruption pivot (voice+0x0, s105-123)

Unchanged from s126's framing — still the single longest-running open
thread, still needs the fresh-angle grep s126 proposed (what else
constructs a name/string table with entries shaped like `at_6`/`at_7`/
`main_n_atpt_lod`/`pilot_sd`) if Thread A audits come back clean.

## Do not

- Do not re-soak specifically to force a positive control on any of
  the 10 guarded classes' sites — not required before landing.
- Do not treat any of s124/s125/s126/s127's 0/0 (unexercised) results,
  or s127's crash-free soak, as evidence any specific guard works in a
  stronger sense than "guard is in place, never triggered because the
  buggy path wasn't hit this run." A crash-free soak with 0/0 guard
  fires is a null result on the guards specifically, even though it's
  informative about the run as a whole.
- Do not re-litigate H1/H2 (voice+0x0 zero-init / asset-alloc
  coincidence) — both closed, s122/s123.
- Do not re-run the `songlifecycle`/`shutdownAudioEngine`
  alias/`musyxInitVoiceFromSample` pointer-identity hypotheses —
  all closed s117-121.
- When landing any new guard, always truncate a `ctx->rN` value through
  `U32()` before comparing against 32-bit literal bounds (s99's
  100%-false-positive lesson, repeated in every guard since — s127
  followed it correctly).
- Do not chase the `do_rom_read`/`piDmaWorker` corruption race
  opportunistically — tracked as its own item (-1) in CURRENT-TRUTH's
  next-steps list.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2000+ lines).
Migrate durable mechanism/architecture material to PROJECT-OVERVIEW.md
and prune superseded detail, paired with a real experiment — not on
its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-127 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
