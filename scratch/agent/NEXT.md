# NEXT work unit — gate1/2/3's measured "taken"/reachability rate (~23-24) can't reconcile with the tick-producer functions' own measured entry count (37); find the measurement error

## Status note (s324): carried forward unchanged — s324 was a MAINTENANCE iteration

s324 was a `docs/CURRENT-TRUTH.md` maintenance pass (Step 0 of `tools/agent/ITERATION.md` triggered at
61,410 bytes); no experiment ran against this hypothesis and nothing below changed. The compaction folded
the s313-322 narrative into a single Next-steps item (now `-173..-181` in `docs/CURRENT-TRUTH.md`) but
touched no facts, no numbers, no conclusions — everything cited below (s317/s320/s321/s322/s323 findings)
is still accurate and still keyed to those session numbers. This work unit is exactly what s323 left
queued. Per iron rule 8, a maintenance-only iteration does not consume one of the 3 allowed consecutive
iterations on a hypothesis-id — the next iteration that actually runs an experiment against this id is
still the 2nd, not the 3rd.

## Context — s323 proved there is no unlocated call site, static or dynamic

s317/s321 (exhaustive text grep) and s323 (a NEW runtime instrument, positive-controlled) together prove
the ONLY 3 places in the entire codebase that can call `tickAllActiveSongs`/`tickAudioSequencerFrame` are
gate1/gate2/gate3 inside `musyxSynthFrame` (`funcs_24.c`). s323's instrument
(`rs64_log_tickfunc_caller` in `lib/N64ModernRuntime/librecomp/src/overlays.cpp`, env
`ROGUESQ_LOG_TICKFUNC_CALLER`) hooks `get_function()` — the resolution point for every `LOOKUP_FUNC`
indirect call in the recompiled code — and found ZERO hits on either target address in a run where a
live positive control (musyxSynthFrame's own known-indirect invocation) fired 40/40 in the same log. This
closes the "unlocated call site" framing that drove sessions s303-322 for good.

**The problem now**: gate1's measured "taken" (call) branch rate is ~19/40, gate2's is ~4/4 (all its
*reached* iterations take the call), gate3 is 0/40 reached at all — combined ~23-24 real call events per
run. But the tick-producer functions' own entry diagnostics ([tick-audio-seq]/[reach-allsongs-entry]/
etc.) independently measure **37** real entries in the SAME run. Since s323 proved no other call
mechanism exists, gate1+gate2+gate3's combined real call count MUST equal 37 exactly — meaning the
measurement of "taken"/"reached" itself is undercounting by ~13-14, somewhere in gate1, gate2, or gate3.

## The work unit — pure source-read first, build+soak only if source-read doesn't resolve it

1. **Re-read gate2's reachability logic specifically** (`fixup_game_funcs.py`'s `_musyx_gate2_patch`,
   `funcs_24.c` around guest 0x80091534). Only 4-5 of gate2's containing-loop iterations were EVER
   sampled as "reached" in any prior soak (s316-320) — check whether gate2's own outer loop bound (the
   `<0x10` comparison against a fixed constant, per s322's trace) could itself be gated by a
   register that's read STALE relative to gate1's loop having already advanced the shared voice cursor
   (`r19`) — i.e. a s318-class TOCTOU on the REACHABILITY count itself (not the taken_skip field, which
   s318 already fixed), where gate2's diagnostic's own entry point is placed somewhere that undercounts
   real loop iterations.
2. **Re-read gate3's diagnostic PLACEMENT specifically** — s322 proved gate3's *guard register* (`ctx->r20`)
   is unclobbered and its narrow reachability window is real game-state-dependent control flow. But s322
   did NOT check whether the diagnostic PRINT STATEMENT itself sits at the right point to catch every
   entry into gate3's loop BODY (as opposed to just gate3's entry guard) — if gate3's loop can be entered
   and iterate multiple times per outer call, and the diagnostic only samples once per outer call (not
   once per inner iteration), that would systematically undercount. Compare against gate1's own diagnostic
   placement (known-correct, cross-validated 1:1 against musyxSynthFrame's own entry count in s320) for a
   structural difference.
3. **Check whether "taken" undercounts multi-call events** — re-verify (don't just cite s321's finding)
   that a single "taken" branch really invokes tickAllActiveSongs/tickAudioSequencerFrame exactly ONCE,
   not inside a loop that could invoke it multiple times per "taken" sample, for gate2 and gate3
   specifically (s321 checked this for gate1's call site only).
4. **If source-read doesn't find the discrepancy**, this needs a build+soak: add a per-gate call COUNTER
   (not just a 40-sample-capped diagnostic) that increments unconditionally every time each gate's real
   call branch is taken, with no sampling cap, and print the FINAL total at process exit or every 128
   calls — compare the 3 gates' summed total directly against the tick-producer functions' own summed
   entry count in one soak. This directly tests whether under-sampling (the `n<40||(n%128)==0` cap
   itself, applied differently to "reached" vs "taken" counters) is hiding additional real events, the
   same bug class already found and fixed 3 times in this investigation (s312/s313/s315) — check this
   FIRST, cheaply, since it is the single most likely explanation and requires no new game-state
   understanding, only re-reading the exact patch definitions.

## Expected discriminating outcomes

- If gate2 or gate3's diagnostic placement is found to systematically undercount real loop iterations
  (steps 1-2): that's the answer, no build needed — write it up, and consider whether fixing the count
  reconciles combined-gates-taken with tick-producer-entries exactly (37) as a confirming cross-check.
- If step 3 finds a per-taken-event multi-call loop in gate2 or gate3's call site: that's the answer.
- If none of steps 1-3 finds an obvious placement/sampling bug, step 4's soak either (a) shows the 3
  gates' real totals DO sum to 37 once uncapped (confirming a sampling-cap illusion, the 4th instance of
  the same bug class), or (b) still falls short of 37 even uncapped — which would be a genuinely new,
  harder mystery (worth a fresh hypothesis-id at that point, not a continuation of this one).

## Environment notes (carried forward from s321/s322/s323, still valid)

- Regen paths for game-code patches are in `/Users/williambuckley/Documents/Tools/N64Recomp`
  (`fixup_game_funcs.py`, `RecompiledFuncs/*.c`, `build/N64Recomp`, `rogue_squadron.toml`), NOT this
  repo. The new `rs64_log_tickfunc_caller` hook lives in THIS repo's
  `lib/N64ModernRuntime/librecomp/src/overlays.cpp` (a `lib/` submodule) — any further edits there need
  `submodule-patches/export.sh` + a commit in the SAME session or they are lost at the next reset.
- If a build/soak turns out to be needed: regen order is `make_elf.py` -> `N64Recomp` ->
  `fixup_game_funcs.py` -> `cmake`, in that exact order (`N64Recomp` skips files that already exist on
  disk — item -20 — so `RecompiledFuncs/*.c` MUST be deleted before every `N64Recomp` run). `cd` into
  `N64Recomp` FIRST as its own bare `cd` command, THEN run `./build/N64Recomp rogue_squadron.toml` with
  output redirection in a SEPARATE Bash call. `/tmp` is blocked for redirects — don't redirect there.
- To reverse ONLY `setDisplayMode`'s site (not `reapplyDisplayMode`'s): narrow the shared regex in
  `fixup_game_funcs.py` (~line 173-174) from `0x8008E(?:B40|C88)` to `0x8008EC88` ONLY (this leaves B40 —
  setDisplayMode — unmatched/unpatched, i.e. reversed; C88 stays force-zeroed). **The prior NEXT.md text
  describing this as "narrow to B40 only" was WRONG** — verified directly against the code and its own
  session-history comments (s319/s320/s323 all narrow to C88-only); trust the code, not a paraphrase.
  MUST restore the full `(?:B40|C88)` alternation before ending session, verified via `audio gate patched
  x2` in the fixup report.
- A NULL result needs a SAME-RUN positive control (iron rule 1) — the existing `[dma-ring-caller]`
  positive control (`ROGUESQ_LOG_DMA_CALLER=1`) does NOT reliably fire in this boot-hang phase (0/0 in
  s323's first soak); use `[tickfunc-caller-control]` (musyxSynthFrame via `ROGUESQ_LOG_TICKFUNC_CALLER=1`,
  already wired, fires 40/40 in this exact phase) instead if this hook is reused.
- `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`
  clears RecompiledFuncs (use the ABSOLUTE path).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.
- Soak driver template: `scratch/s73_post_a_scene/run_step323tickfunccaller.sh` (newest; copy it, don't
  hand-roll — it already arms `ROGUESQ_LOG_TICKFUNC_CALLER`/`ROGUESQ_LOG_DMA_CALLER` alongside the full
  established breadcrumb set). Invoke as `zsh run_foo.sh <label>`, not `./run_foo.sh`. `cd` into
  `scratch/s73_post_a_scene` first as its own bare command. Launch via Bash with `run_in_background: true`,
  then `TaskOutput` with `block: true` and `timeout` up to 600000ms — do NOT foreground-poll. Confirm
  `pgrep -f "build/RogueSquadron64Recomp"` is empty before AND after. Expect `phase timeout (INCONCLUSIVE)`
  after ~600s — this config (setDisplayMode reversed) reliably hangs at VI=320/rdpFs=39 before reaching
  the 1024-width title screen; this is the EXPECTED, established behavior for this soak recipe, not a
  run failure — the log data before the freeze is what matters.
- Multi-operation Bash commands combining `cd`+redirect, or `export VAR=...` chained with other
  commands, trigger permission prompts — issue `cd` as its own bare command, run each `export`/command
  separately.

HYPOTHESIS-ID: m5-audio-destub-step4-tick37-vs-hardstop40 (still 2nd EXPERIMENTAL iteration on this id —
s323 opened it and closed the "unlocated call site" framing; s324 was maintenance-only and does not count
against the budget. Per iron rule 8, if a 3rd consecutive iteration that actually experiments on this id
produces no discriminating result, pivot or go BLOCKED with a specific question next time.)
