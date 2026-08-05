# NEXT work unit — check gate3's CONTAINING conditional for an s318-class read/branch mismatch

## Context — s321 exhaustively ruled out an undiscovered static/simple-indirect call site

s319/s320 confirmed a real, same-run 14-call gap: gate1+gate2's own measured "call"-branch takes (23-24)
fall short of the tick-producer functions' (`tickAllActiveSongs`/`tickAudioSequencerFrame`) own measured
entry counts (37-38). s321 ran the exhaustive grep the prior session planned — direct-call, full-address
data-reference, AND split-halfword address-construction (validated against a known positive control,
`musyxSynthFrame`'s own s310 self-rearm mechanism) — across all of `RecompiledFuncs/*.c`, for BOTH target
functions (only `tickAudioSequencerFrame` had ever been checked this way before, in s317).

**Result: clean, positive-controlled miss on every axis. The recompiled source contains structurally NO
4th call site.** Also re-verified (disassembly read, not just the patch comment) that gate1's "call"
branch really does invoke both target functions unconditionally and sequentially — no internal branching
that could make their counts diverge from each other or from the gate's own tally. And ruled out a
shared-counter double-count bug in the tick-producer diagnostics (each has its own separate static
counter). Full detail: PORTING-STATE Session 321, CURRENT-TRUTH item -180.

**Do not re-run the exhaustive call-site/address grep — s321 settled that as exhaustively as text search
allows.** Two possibilities remain, neither answerable by grep:

(a) A fully dynamic indirect call, resolved through a data structure whose address is computed by an
    expression with no literal split-halfword pair anywhere (e.g. loaded from a runtime-computed pointer
    chain). 28,388 `LOOKUP_FUNC(ctx->rN)` call sites exist across `RecompiledFuncs/*.c` (grep-counted,
    s321) — tracing each one's register provenance by hand is not viable in a bounded session.

(b) gate3's persistent "0/40 reached, its containing code path never entered" measurement might itself
    be unreliable — the SAME diagnostic-methodology class of bug s318 found in gate1/2/3's `taken_skip`
    field (which read a stale, separately-fetched re-read of the shared countdown instead of `ctx->r2`,
    the register the real branch decision actually uses). s318's fix only touched the branch-OUTCOME
    field inside each gate's already-instrumented body — it never questioned whether the CONDITIONAL that
    decides whether gate3's body is entered at all might have the same kind of mismatch (e.g. gating on a
    re-read of shared state rather than the register/flag the real dispatch code actually branches on).

## The work unit

**(b) is the cheaper, higher-information-value check — start here. Pure source-read, no build, no soak.**

1. In `RecompiledFuncs/funcs_24.c` (the standalone `~/Documents/Tools/N64Recomp` checkout, NOT this
   repo), locate gate3's diagnostic block (search `musyx-gate3` or `s_musyx_gate3`) and read the
   disassembly comments/generated C for the ~30-40 lines immediately ABOVE it — the real branch/jump
   structure that decides whether control ever reaches gate3's containing code region at all. This is a
   DIFFERENT question from what's already instrumented (gate3's own countdown/period/reg fields, which
   only fire IF the block is reached) — the goal is the guard/branch that gates reachability itself.
2. Compare that guard against gate1's and gate2's equivalent guards (both of which ARE reached — gate1
   40/40, gate2 4/4). Do all 3 gates share the exact same outer branch structure (e.g. a 3-way dispatch
   inside a loop, a switch, or 3 sequential independent `if` blocks each behind its own separate
   precondition)? If gate3's outer guard is a genuinely different/independent precondition from gate1/2's
   (not just "third case of the same dispatch"), its reachability is a real fact, not a measurement bug —
   in which case this specific lead is dead and the investigation should pivot to accepting (a) as the
   remaining explanation (write up as BLOCKED-on-tooling or deprioritize M5 step 4 per iron rule 8, since
   this hypothesis-id will hit its 16th consecutive session).
3. If gate3's outer guard DOES look like it could diverge from the real dispatch decision the way
   gate1/2/3's `taken_skip` field did (e.g. it also re-reads a shared word freshly instead of using the
   register the real branch uses, or checks a DIFFERENT condition than what the disassembly's actual
   conditional-branch instruction tests) — that is the discriminating find. Characterize it precisely
   (exact mismatch, exact instruction addresses) and write it up; a follow-up session would then fix the
   reachability diagnostic itself and re-soak to see if gate3 turns out to be reached after all, closing
   (or substantially narrowing) the 14-call gap.
4. This step needs NO soak and NO build — it's reading already-generated `RecompiledFuncs/funcs_24.c`
   against the disassembly comments already embedded in it, the same way s318 found its bug (by reading
   source, not by running anything).

**Discriminating outcome**: gate3's outer guard tests the SAME state/register the real dispatch uses
(no mismatch) = reachability is a real fact, this lead is dead, pivot away from grep/read-only steps for
this hypothesis (raise it to the user or scope a NEW instrumentation-based experiment, e.g. sampling
`ctx->r2`/the true dispatch register right at gate3's guard, similar to s318's fix, but this needs a
build+soak this time since it requires NEW instrumentation, unlike s318 which only added a field to
diagnostics that already existed inside the block). Gate3's guard shows a genuine re-read/register
mismatch (an s318-class bug) = a concrete, fixable diagnostic bug, worth its own instrumentation+soak
follow-up next session.

## If this lead also dies (no mismatch found)

Per iron rule 8: this hypothesis-id will be entering its 16th consecutive session with the grep/read
avenues now exhausted. If step 2/3 above finds gate3's guard is legitimately independent (not a
measurement artifact), write the hypothesis/evidence table into a fresh NEXT.md, and consider: (i)
scoping ONE new build+soak that samples the TRUE dispatch register at gate3's outer guard (an s318-class
fix, needs new instrumentation not just a re-read of existing fields) as the next actionable step, or
(ii) explicitly flagging to the user that resolving explanation (a) (a fully dynamic indirect call among
28,388 sites) is out of reach for grep-based investigation and needs either a different tool (e.g.
runtime call-site logging keyed on target address, not text search) or a deprioritization decision.

## Environment notes (carried forward, all still valid)

- Regen paths for game-code patches are in `/Users/williambuckley/Documents/Tools/N64Recomp`
  (`fixup_game_funcs.py`, `RecompiledFuncs/*.c`, `build/N64Recomp`, `rogue_squadron.toml`), NOT this
  repo. Separate checkout from `lib/N64ModernRuntime`'s nested `N64Recomp` submodule — edits here do NOT
  need `submodule-patches/export.sh`. Only edits actually inside this repo's `lib/` need that.
- This work unit (step 1-3 above) is pure grep/read against the ALREADY-CURRENT `RecompiledFuncs/*.c`
  (baseline state, both audio-gate sites force-zeroed) — no regen, no rebuild, no soak needed.
- If a follow-up build/soak turns out to be needed (step 3's positive branch, or the "if this lead also
  dies" fallback (i)): regen order is `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`,
  in that exact order (`N64Recomp` skips files that already exist on disk — item -20 — so
  `RecompiledFuncs/*.c` MUST be deleted before every `N64Recomp` run, not after). `cd` into `N64Recomp`
  FIRST as its own bare `cd` command, THEN run `./build/N64Recomp rogue_squadron.toml` with output
  redirection in a SEPARATE Bash call.
- To reverse ONLY `setDisplayMode`'s site (not `reapplyDisplayMode`'s) if a future soak needs it: narrow
  the shared regex in `fixup_game_funcs.py` (~line 174) from `0x8008E(?:B40|C88)` to `0x8008EC88` only.
  MUST restore the full `(?:B40|C88)` alternation before ending session, verified via `audio gate patched
  x2` in the fixup report.
- `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`
  clears RecompiledFuncs (use the ABSOLUTE path).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.
- Soak driver template if needed: `scratch/s73_post_a_scene/run_step320synthentryvsgate1.sh` (newest;
  copy it, don't hand-roll). Invoke as `zsh run_foo.sh`, not `./run_foo.sh` (bare `./run_*.sh` gets
  denied). `cd` into `scratch/s73_post_a_scene` first as its own bare command. Launch via Bash with
  `run_in_background: true`, then `TaskOutput` with `block: true` and `timeout` up to 600000ms — do NOT
  foreground-poll. Confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty before AND after.
- `/tmp` is blocked for redirects — use a path inside this repo, `N64Recomp`, or `rogue_squadron64`
  instead.
- Multi-operation Bash commands combining `cd`+redirect, or `export VAR=...` chained with other
  commands, trigger permission prompts in this sandbox — issue `cd` as its own bare command, and run
  each `export`/command separately rather than chaining with `&&` or newlines in one call.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-321 — still the active
investigation thread. 15 of these sessions have each produced a discriminating result in sequence
(s303/s306/s307/s309/s310/s311/s312/s313/s315/s316/s317/s318/s319/s320/s321), resetting the iron-rule-8
no-progress counter every time; s314 (maintenance) doesn't count. Continue the same slug next
non-maintenance session — but per the "if this lead also dies" section above, be ready to pivot the slug
if step 2/3 finds gate3's reachability is legitimate (not a measurement artifact), since the grep/read
avenues are now exhausted and the remaining explanation (a fully dynamic indirect call among 28,388
sites) is not tractable by the same methodology.
