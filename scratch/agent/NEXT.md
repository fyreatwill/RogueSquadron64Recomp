# NEXT work unit (s1888)

HYPOTHESIS-ID: vi1024-reachability-regression

s1888 found that VI width 1024 — reached reliably at ~79.5-79.8s in every
`s790_postsec2_reachability` soak from s815 through s844 (2026-08-13) — is
not reached at all in 5/5 fresh runs today (2026-08-17), including one
byte-for-byte unmodified run of `scratch/agent/s790_postsec2_reachability.sh`.
The attract sequence now stalls indefinitely at VI width 640, origin
`0x00696100` (confirmed stuck to 340s of real wall-clock wait, so it is not
merely slower than before). 2 of the 5 runs additionally hit a new native
crash before that stall, in `RT64::NativeTarget::copyToRAM` (inside
`RT64::State::fullSync` / `RT64::Framebuffer::copyNativeToRAM`), with
`last-guest-pc=0x80001f88`.

This blocks the hangar/512 M4 revisit (parked UNEVALUABLE again, s1872 +
s1888, now for an upstream reason) and the entire
`s790_postsec2_reachability` soak family, which underpins a large fraction
of the project's M3/E9-provenance evidence base. No `lib/` or source edits
were made in s1888 — this is not that session's own artifact.

## Competing hypotheses

- H1-flake: this is ordinary run-to-run nondeterminism (the project has
  documented other nondeterministic outcomes downstream of SELECT CRAFT) and
  5/5 today was bad luck. A clean re-run of the unmodified script should
  succeed at least once in a small batch.
- H2-build-drift: something in the current build differs behaviorally from
  the s815-s844 build, despite no ledgered source changes in between —
  candidates: a stale/regenerated `RecompiledFuncs/*.c` tree from an
  intervening regen, or a `lib/` submodule patch (`submodule-patches/*.patch`)
  drift versus what s844 actually ran against.
- H3-machine-state: something about *this* machine's current state (thermal
  throttling, background load, a stale window/socket) is slowing or wedging
  the attract loop specifically at `0x00696100`, not a code regression.
- H4-real-regression: an actual logic change (in this repo's source, in a
  `lib/` patch, or upstream in a submodule bump) broke the transition out of
  the second 640 phase. Distinguishing this from H2 needs a bisect.

## Discriminating measurement

1. Re-run the **unmodified** `scratch/agent/s790_postsec2_reachability.sh`
   2-3 more times, back to back, one game at a time, SIGKILL between runs.
   - If any run reaches VI 1024 (grep `run.log` for
     `[phase] vi_width=1024`): H1-flake gains support. Compute a hit rate
     (e.g. "2/5 combined") and decide whether the soak family is merely
     degraded (queue it with a retry budget) or still broken often enough to
     block work.
   - If all runs stall at `0x00696100` again: H1 is refuted; move to step 2.
2. If still stuck, check for the boring things first (iron rule 5) before
   assuming H4:
   - `git -C lib/N64ModernRuntime status --short` / `git -C lib/rt64 status
     --short` — compare against what this session already confirmed (the
     standing uncommitted patch set, unchanged). If it now differs, something
     new landed there uncommitted.
   - `ls -la build/RogueSquadron64Recomp` — confirm the binary mtime; if a
     regen happened between s844 and now, check whether
     `tools/fixup_game_funcs.py` / `tools/fixup_factor5_ucode.py` changed
     (`git log --oneline -- tools/fixup_*.py` since 2026-08-13).
   - `top`/`ps` during a run — rule out CPU/thermal contention concretely
     (not just "looked idle") while the game is stuck at `0x00696100`.
3. Only after ruling out H1-H3 with actual evidence (not just "no changes in
   git log") should this be escalated to a bisect (H4): pick a commit near
   s844's date, temporarily build the game from that state in a way that does
   not touch the tracked working tree (e.g. `git worktree add` at that commit
   plus a scoped rebuild), and check whether it reaches 1024. This is
   expensive — do not jump straight to it.

## Exact commands

```
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
zsh scratch/agent/s790_postsec2_reachability.sh   # repeat 2-3x, one at a time
grep -a '\[phase\] vi_width=1024' <outdir>/run.log  # presence = reached
```

## If the regression re-confirms and no cause is found in one more session

Budget rule (iron rule 8) applies to this HYPOTHESIS-ID same as any other:
after 3 consecutive non-ADVANCED iterations on `vi1024-reachability-regression`,
write the hypothesis/evidence table into this file and pivot — either back to
the generated-symbol sweep (leftover `func_800F2AC4`, `docs/CURRENT-TRUTH.md`
next-step 2) or to a fresh angle, and leave this regression filed as a named,
open blocker rather than chased indefinitely.

Do not re-open the hangar/512 H-* table (H-clip-reject / H-zero-height-emit /
H-on-screen-emit / H-never-live) until a run actually logs
`[phase] vi_width=1024` again.
