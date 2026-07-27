# NEXT work unit — M3: reproduce the `advancePlayerAnimationPhase` SIGBUS with the s88 instrument live

s87 found an 8th crash class (SIGBUS, two identical consecutive frames
`advancePlayerAnimationPhase + 2572`) and guessed a mechanism (self-
recursion via a callback slot at guest `0x80139968`). **s88 refuted that
specific mechanism at the source level**: the call site s87 cited
(`0x8006426C`) belongs to a *different* function, `invokeMenuOverlayHeaderCallback`,
never reached from `advancePlayerAnimationPhase`'s own body —
`advancePlayerAnimationPhase` has zero indirect calls of its own (checked
by reading its full C body, `N64Recomp/RecompiledFuncs/funcs_14.c:4029-4331`
after a fresh regen — only two direct `jal`s, both to
`activateAnimationKeyframe`, whose own callees make no further calls).

s88 landed a **correctly-targeted** instrument instead:
`ROGUESQ_LOG_ANIM_CB=1` logs guest `$sp` (`ctx->r29`, a depth proxy) +
`arg_r4`/`arg_r5`/`ra` at the function's own entry
(`N64Recomp/fixup_game_funcs.py`, new `_anim_cb_patch` block — **not**
`lib/`, no `submodule-patches/export.sh` needed). It fired 3296/3296 in
one soak (positive control confirmed) — but **that soak never crashed at
all** (first crash-free soak since s83, all 8 known classes, 0 fires).
So the instrument is proven to work but has never yet been observed
during an actual crash.

## Do first, before running anything

Check whether the last soak's clean run was a fluke or the new normal:
run the exact same soak shape again. If it stays clean 2/2, that's itself
an important data point (see "If it stays clean" below) — don't just
keep re-running hoping for a crash without updating the docs to reflect
that.

## Competing hypotheses (unchanged from s87, now better-instrumented)

1. **Self-recursion via *some* corrupted pointer/data**, just not the one
   s87 guessed — e.g. `activateAnimationKeyframe`'s track-walk (its
   symbol comment: "Recursively walks track at *(a1+0xC)") hitting a
   corrupted or cyclic pointer chain that eventually calls back through
   `advancePlayerAnimationPhase` via a route not yet traced. `$sp` would
   start moving away from its normal ~6-value band in the calls
   immediately before a crash.
2. **Not stack-depth recursion at all.** The crash trace's two identical
   frames could be a **symbolication artifact**: if the true fault is a
   wild `MEM_W`/`MEM_B` write in inlined code, or if the unwinder's
   frame-pointer walk got confused by a corrupted/overwritten frame, it
   can print the same nearest-preceding-symbol twice without real
   recursion. `$sp` would stay flat (like this run) right up to the
   crash — consistent with "the bug is a bad memory write somewhere in
   this function's body or its inlined callees, not unbounded recursion."

## Command

```
env ROGUESQ_LOG_ANIM_CB=1 PROBE_MODE=start_only HOLD_S=30 zsh \
  scratch/s73_post_a_scene/run_mission_keys.sh animcb2 0 12
```
(reuses the build from s88 — no regen needed unless you change the
instrument itself.)

## Discriminating measurement

1. `grep -c CRASH scratch/s73_post_a_scene/animcb2/run.log` — if 0 again,
   this is now 2/2 clean vs. 5/5 crashing (s83–s87). That asymmetry is
   itself worth a documented conclusion: either something changed between
   s87 and s88/s89 (check: was anything about the build, env, or timing
   different?), or the crash really is a low-probability race and 30s
   holds aren't long enough to reliably hit it — in which case, consider
   a longer `HOLD_S` (e.g. 90) or running back-to-back soaks to build a
   crash/no-crash ratio before spending another iteration guessing at
   mechanism from a single crash log.
2. If it crashes: `grep -n CRASH` for the line number, then look at the
   ~20 `[anim-recurse]` lines immediately before it.
   - `sp` flat (same handful of values as the rest of the run) right up
     to the crash → hypothesis 2 supported (not real recursion; look for
     a wild-write signature elsewhere — e.g. check `arg_r4`/`arg_r5` at
     the last entries for garbage-looking pointers, and consider adding
     a similar entry log to `activateAnimationKeyframe` next).
   - `sp` drops sharply and repeatedly in the last N entries (genuine
     nested growth) → hypothesis 1 supported; that's real recursion and
     worth checking whether `arg_r4` repeats (same slot pointer calling
     itself) or advances (walking a corrupted/cyclic linked structure).

## Do not

- Do not re-guess a specific call site from a line-number grep without
  confirming which `RECOMP_FUNC` block the lines belong to — that's
  exactly the mistake s87 made and s88 spent most of its budget
  correcting.
- Do not hand-edit `N64Recomp/RecompiledFuncs/funcs_14.c` — the
  instrument lives in `N64Recomp/fixup_game_funcs.py` and is idempotent
  across regens.
- If using a function `repl` in `re.subn` (as `_anim_cb_patch` does),
  remember this sidesteps `re.sub`'s replacement-template backslash
  processing — plain Python string escaping applies as normal. If you
  instead write a raw-string template (the style used elsewhere in this
  file), remember `\\` collapses to `\` there and `\'`/`\"` do **not**
  behave the way they look; read the generated C back before building,
  not just after a successful compile (the s88 bug compiled fine on
  the buggy first attempt — nothing caught the mangled quotes until the
  file was read).
- Budget: this is iteration 2 of the ITERATION.md rule-8 budget on the
  anim-recursion hypothesis family (s87: 1 refuted guess; s88: 1
  correctly-targeted but crash-free run). One more inconclusive result
  (crash-free again, or a crash whose `[anim-recurse]` data doesn't
  discriminate) and reassess — either fall back to characterizing this
  as a rare/unrepducible one-off and move to next-steps item 2 (TMEM-
  zero assert) or item 3 (shared-race retest), or go BLOCKED with the
  specific question "does this crash reproduce at all outside s87's one
  observation."

## If items 1-style soaks keep coming back clean

Consider whether the s84 thr-resume gate (now validated, U3 closed) or
some other recent change incidentally reduced how often *any* of the 8
crash classes fires — worth a quick same-run check of whether `bad_total`
and `[rom-read]` corruption rates look different across the last few
soaks (s85/s86/s87/s88) rather than assuming the anim-recursion bug
specifically got harder to hit.
