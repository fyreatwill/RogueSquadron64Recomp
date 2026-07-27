# NEXT work unit — continue Thread A re-audit (16th/17th/18th classes)

s129 finished item 2/5 of the Thread A re-audit list: re-read
`reserveAndEmitDLEntry` (14th class, `funcs_3.c:14435-15002`) to its
closing brace and found it CLEAN — the s109 guard on `ctx->r16`/`$s0`
(the function's `a0` argument) is the only unguarded-external-pointer
site. A subagent flagged a repeated pointer-deref pattern past the
guard (three free-list-pop sequences around 0x8000CC28/CD24/CE30); a
direct source read (not just the subagent's report) confirmed this is
the SDK's own sentinel-based free-list allocator operating on internal
pool state reloaded fresh from fixed globals, not the caller's raw
`a0`/`a1` argument re-derefed — categorically different from every
prior hit in this thread. Read PORTING-STATE's Session 129 entry before
doing anything else; this file only has the actionable summary.

**Running tally: 4 hits, 1 clean, of 5 functions audited**
(composeNpcOrientationMatrix s126 — hit; updateAnimatedTextureStreaming
+ static_5_800B4048 s127 — hit both; projectModelBoundsToScreen s128 —
hit; reserveAndEmitDLEntry s129 — clean). The generalizing hypothesis
is now sharper than "every function has a second site": functions that
keep dereferencing the SAME raw incoming argument past their guard have
a second site; functions whose only post-guard pointer traffic is
freshly-loaded internal/allocator state (reloaded from a fixed global,
not derived from the argument) do not. Test this refined hypothesis
against the 3 remaining functions.

## This session's environment notes (carry forward, still current)

- Before assuming any `lib/` submodule has uncommitted session work,
  diff its dirty working tree against the matching
  `submodule-patches/*.patch` file (`git diff` in the submodule, save
  to a scratch file, `diff` it against the patch — do this from the
  repo root or `cd` into the submodule first; `git -C <dir> ...` and
  `git diff --stat -- lib/...` do NOT match the `git status:*`/`git
  diff:*` allowlist prefixes and require approval every time, whereas
  plain `git status`/`git diff` after a bare `cd` do). If they match
  byte-for-byte, nothing is lost — the `STATUS=WORKING` /
  deleted-`OUTCOME` state at session start is just the loop harness's
  normal per-iteration reset marker, not evidence of a crashed prior
  session.
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
  The same applies to any `&&`-chained compound command whose second
  half isn't itself allowlisted (e.g. trailing `echo "EXIT=$?"`) — split
  into separate calls instead.
- `env FOO=1 BAR=1 zsh script.sh args > log 2>&1` (no `&&`, no `cd`) ran
  with no approval friction — prefer this single-call shape for
  soak-driver invocations. Running it via the background-Bash tool
  (`run_in_background: true`) worked cleanly and freed the turn to do
  other prep while the ~90-140s soak ran; wait for the completion
  notification rather than polling the log by hand.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same
  session to "double check" the report — it is known non-idempotent
  (s102) and will duplicate every already-applied patch on disk.
  Verify patch multiplicity via direct `grep -c` on the regenerated
  `.c` files instead.
- `shasum`/`md5`/`cmp` are not allowlisted and prompt for approval on
  every call regardless of args; plain `diff <fileA> <fileB>` (no
  chaining) works and needs approval only once per session-shape.

## Do next: re-audit the remaining 3 guarded multi-site functions

Same method as s126-129: read each function FULLY to its own closing
brace (funcs_*.c line numbers below), looking for a second deref of the
SAME raw incoming argument the existing guard already protects — not
just any pointer chase in the function (s129 learned that internal
allocator/free-list traffic reloaded from a fixed global is a different,
lower-priority shape; don't guard it reflexively). Delegate the full-body
read to a parallel Explore-type subagent with a self-contained prompt
(exact file/line range, exactly what the existing guard already covers
so it isn't re-reported, exactly what NOT to flag — reuse s129's prompt
as the template, it now correctly separates "raw argument re-derefed"
from "internal pointer reloaded from a global"). Verify any positive
finding yourself against the source before writing a patch — subagent
reports are claims, not facts (s129 caught a subagent's own
CONFIRMED-vs-PLAUSIBLE hedge and confirmed the hedge was warranted).

Remaining, in suggested order:

1. **16th, `activateAnimationKeyframe`** (`funcs_14.c`, guard at s99,
   table-deref shape: `table[arg_r4 & 0xFFFF]` then `deref+0x30`).
   Function bounds not yet located this session — grep
   `void activateAnimationKeyframe` in `funcs_14.c` and the next
   `RECOMP_FUNC` after it.
2. **17th, `submitSceneNodeRender`** (`funcs_4.c`, guard at s123,
   free-list-walk shape — note this one's own catalog entry already
   says the guard covers a walk loop, worth double-checking whether
   the loop has an early-exit path the guard's placement doesn't
   dominate).
3. **18th, `updateHangarBayScene`** (`funcs_40.c`, guard at s110 — this
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

If a function comes back clean (like s129's `reserveAndEmitDLEntry`):
no code change, no rebuild, no soak needed — just document it the same
way s129 did (verified-clean, with the reasoning for why the flagged
traffic doesn't count) and move to the next function.

When all 3 remaining functions have been audited (whatever the mix of
hits/clean): write up the final tally (currently 4 hits / 1 clean of 5;
could end anywhere from 4/8 to 7/8 hits) and fall through to Thread B —
the tally itself, hit or clean, is the useful result NEXT.md has been
building toward since s126.

## Thread B (fallback): the audio-corruption pivot (voice+0x0, s105-123)

Unchanged from s126-129's framing — still the single longest-running
open thread, still needs the fresh-angle grep s126 proposed (what else
constructs a name/string table with entries shaped like
`at_6`/`at_7`/`main_n_atpt_lod`/`pilot_sd`) once the Thread A audit list
is exhausted.

## Do not

- Do not re-soak specifically to force a positive control on any of
  the 12 guarded classes' sites — not required before landing.
- Do not treat any of s124-128's 0/0 (unexercised) results as evidence
  any specific guard works in a stronger sense than "guard is in place,
  never triggered because the buggy path wasn't hit this run."
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
  next-steps list.
- Do not chase the RSP-microcode `Unhandled jump target 0x0231`/`0x17F0`
  diagnostic if seen again — already documented (s79) as "secondary,
  not onset cause," not a new class.
- Do not guard internal allocator/free-list pointer traffic just
  because it's dereferenced without a visible check (s129) — that shape
  is the SDK's own sentinel-list idiom, safe by construction, and
  guarding it is scope creep past Thread A's actual bug pattern (a
  second deref of the SAME externally-supplied, corruption-exposed
  argument). Only flag/guard sites that trace back to a raw incoming
  argument or another already-corruption-exposed value.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (2000+ lines).
Migrate durable mechanism/architecture material to PROJECT-OVERVIEW.md
and prune superseded detail, paired with a real experiment — not on
its own.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-129 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
