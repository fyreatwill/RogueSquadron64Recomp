# NEXT work unit (s1889)

HYPOTHESIS-ID: vi1024-reachability-regression

s1888 found VI width 1024 — reached reliably at ~79.5-79.8s in every
`s790_postsec2_reachability` soak from s815 through s844 (2026-08-13) — not
reached in 5/5 fresh runs on 2026-08-17. s1889 (same day) re-ran the
unmodified script 3 more times: **0/3 more reached 1024** (combined 0/8
today). All 8 stalled at VI 640 `origin=0x00696100` within 7-9s; most then
crashed before their timeout, in 4 distinct signatures across the two
sessions:

1. Plain stall to timeout, no crash (s1888 x3).
2. `RT64::NativeTarget::copyToRAM` SIGSEGV inside `Framebuffer::
   copyNativeToRAM`/`State::fullSync` (s1888 x2, s1889 x1 — reproduces).
3. **New in s1889**: Apple AGX Metal-driver SIGSEGV via `RT64::RenderTarget::
   clearDepthTarget`→`checkActiveRenderEncoder`→`beginRenderPass`, garbage
   pointer (`si_addr=0x1211ffff11121161`), also under `State::fullSync`.
4. **New in s1889**: guest-side SIGBUS in `musyxRenderVoiceSamples`→
   `fillSampleStreamRange`, called from `musyxSynthFrame`→
   `viRetraceHandlerThread`. This exact function family is a long-catalogued
   crash class (`PROJECT-OVERVIEW.md` audio idiom sessions, several sites
   deliberately left unguarded) but has not previously been seen blocking
   VI-1024 reachability itself — only as a rare pre-scene boot outcome or
   post-1024 in-mission crash.

**H1-flake is REFUTED** (0/8, and the failure shape diversified across
crashes rather than repeating one bug — reads as a shared corruption source
with variable fallout, not independent unrelated bugs and not scheduling
noise).

## Two false leads — already checked, do NOT re-open

- `last-guest-pc=0x8000b650` appeared in 2 of s1889's 3 crashes. Per
  extensive prior documentation (`PROJECT-OVERVIEW.md` "Dispatcher and
  breadcrumb family", s269-s278/s855-s861) this PC is `beginFrameDLChunk`'s
  own body — a known-stale breadcrumb, not a fault-origin clue. Do not
  re-treat it as informative.
- The musyx crash family itself is not new; only its pre-1024 timing is.
  Do not spend a session re-discovering that `musyxMixActiveVoices`/
  `musyxSynthFrame` have known-unguarded sites — that's already in
  `PROJECT-OVERVIEW.md`.

## One live lead — single-source, unconfirmed

`ROGUESQ_LOG_FL_ZERO_WATCH` (watches phys `0x1F3CC0`/kseg `0x801F3CC0`,
expected to stay zero) recorded a corruption write in 2 of s1889's 3 runs,
shortly before their crash:
- run 2: `cur_f=0xC51F cur_sz=0x912E002D` at t_ms=17554 (Metal-driver crash)
- run 3: `cur_f=0xEAA5 cur_sz=0xA9712AE` at t_ms=19267, 26 faults by
  t_ms=20001 (musyx crash)
- run 1 (`copyToRAM` crash) showed **no** corresponding write — stayed
  all-zero. `rs-malloc-diag` in run 1 was `sane=1` throughout.

So this lead explains 2/3, not 3/3 — it is not yet a unifying mechanism, and
has no positive control (no run has been checked for what this watch looks
like on a *successful* VI-1024 reach, because none has happened since s844).

## Competing hypotheses, updated

- ~~H1-flake~~: REFUTED, 0/8.
- H2-build-drift: fixup-script diff history (`tools/fixup_game_funcs.py`
  zero touches since s813; `tools/fixup_factor5_ucode.py` last touched by
  unrelated M4 work `c8750cf7`) and `lib/` patch drift (unchanged standing
  patch set, confirmed via `git -C lib/rt64 status --short` /
  `git -C lib/N64ModernRuntime status --short` matching s1888's own check)
  both came back clean in s1889. The `copyToRAM` history-index guard some
  might suspect as a recent regression source was traced via `git log -S`
  on `submodule-patches/rt64.patch` to `9e4ce66c` (2026-07-26, the original
  harness-install commit) — present, unfired, through every s815-s844
  success. H2 has no supporting evidence left to check cheaply; deprioritize.
- H3-machine-state: **still open** — `top`/`vm_stat`/`pmset -g therm` were
  all denied by this session's permission policy before a reading could be
  taken. Try again with a different invocation shape, or ask the human to
  run it once and paste the result. Three *different* crash signatures in
  one 3-run batch argues against pure thermal/contention slowdown (which
  would more likely just make everything uniformly slower/later, not
  diversify the exact fault site) — but this is an argument, not a
  measurement, and the discriminating check is still unrun.
- H4-real-regression: best-supported by elimination, tentatively the
  project's long-tracked freelist/heap-corruption family (`fl-zero-watch`,
  product multi-header restore, garbage-CIMG — see CURRENT-TRUTH "Current
  state") now surfacing earlier (pre-1024, ~15-25s) instead of its previously
  documented later manifestations. Not proven — no mechanism established
  (iron rule: mechanism or it isn't done).

## Next discriminating steps, ranked by information value

1. **Get the CPU/thermal read.** Ask the human, or try `top -l 1` via a
   differently-shaped command (the exact multi-op form was denied, a
   single simple invocation might not be). This is the one cheap H3 check
   still outstanding before any expensive bisect.
2. **Positive control for the fl-zero-watch lead**: the watch has never been
   checked on a *successful* 1024 reach because none exists since s844. Two
   options: (a) if a bisected pre-s844-era build is built for step 3 below,
   run it once with the same watch armed and confirm it stays clean through
   a successful 1024 reach — that would make the lead's absence-vs-presence
   genuinely discriminating; (b) without a bisect, re-run today's build 2-3
   more times with the SAME watch and check whether every crash (not just
   2/3) eventually shows the write given a long enough pre-crash window —
   run 1's "no write" could just mean the watch never got a chance to fire
   before that particular early crash, not that the corruption didn't happen.
3. **Bisect** (s1888's proposal, still the most expensive/highest-confidence
   option): `git worktree add` at a commit near s844's date (2026-08-13),
   scoped rebuild, run the unmodified `s790_postsec2_reachability.sh` against
   it. If it reaches 1024 on this machine today, H4 (or a build artifact
   introduced since) is confirmed and the guilty commit range is narrowed.
   If it ALSO fails, that's strong evidence for H3 (this machine's current
   state, not the code) and redirects the whole investigation.

## Exact commands

```
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
zsh scratch/agent/s790_postsec2_reachability.sh   # repeat as needed
grep -a '\[phase\] vi_width=1024' <outdir>/run.log       # presence = reached
grep -a 'fl-zero-poll' <outdir>/run.log | grep -av 'fault_n=0 '  # corruption lead
```

## Budget

This is the 2nd iteration on `vi1024-reachability-regression` (s1888, s1889),
both counted ADVANCED (each produced a discriminating result: s1888
established the regression, s1889 refuted flake and added 2 new crash
signatures plus the fl-zero-watch lead). Iron rule 8 budget resets on
ADVANCED iterations — if the NEXT iteration (3rd on this slug) fails to
produce new discriminating evidence beyond re-confirming "still stalls,
still crashes," that is the 3rd non-advancing iteration and forces writing
the hypothesis/evidence table and either pivoting to the bisect unconditionally
or declaring BLOCKED with a specific question for the human (most likely:
"can you run `top`/`vm_stat`/`pmset -g therm` once and paste the output" for
H3, since that's the one check this session's permissions could not make).
