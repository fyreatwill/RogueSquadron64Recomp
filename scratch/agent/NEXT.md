# NEXT work unit

## s337 closed the cinematicLoopBody-exit-gate question — start here

s337 (`HYPOTHESIS-ID m5-audio-destub-cinematicloopbody-divergent-callees`, 3rd of 3 iterations, iron
rule 8 budget exhausted, CURRENT-TRUTH item -194, full detail `PORTING-STATE` Session 337) ran the
runtime instrument NEXT.md's step 1 asked for: 3 diagnostics on `static_6_800AF550`
(`ROGUESQ_LOG_CUTSCENETIMER_REACH=1`), soaked with `ROGUESQ_LOG_MAINGAMELOOP_REACH=1` armed alongside.

**Findings**: the delta-time input (`a2`) advances normally the entire run (0.0167-0.0333, never
frozen) — refutes "OS clock not advancing." But the global pointer at `0x800B0934` the function
depends on stayed **NULL for ~89% of the run** (n=1 through n=1024 of 1152 total calls) — the real
threshold/debounce logic never ran for virtually the whole stall. Only at the very last logged call
(n=1152) did the pointer go non-null; the debounce counter then completed in one tight 7-call burst
right at the log's tail, and the function's one real "exit" signal (`return 1`) fired exactly once.
**But `[vi-fs-decision]` kept logging `stalled=1 pairs=0` at the identical VI address for the ~4283
remaining log lines through the log's end** — the exit firing did not visibly clear the graphics-task
stall this whole investigation was opened to explain.

## New question: is `cinematicLoopBody`'s exit gate even relevant to the VI=640 stall at all?

s336 already established that `cinematicLoopBody`'s internal loop calls **`submitGfxFrame` directly,
every iteration** (`funcs_27.c:108253`) — a completely separate graphics-producer call from the whole
`runVideoFrameTick`-callers chase s333-s336 spent 4 sessions on. If `submitGfxFrame` is the actual
per-frame graphics-task producer during this phase (not `runVideoFrameTick` via any of its 5 callers),
then the entire `mainGameLoop`/`cutsceneDispatchSlotsByFlag`/`static_6_800A9ABC` reachability
investigation may have been chasing an irrelevant call chain from the start, and the real question is
narrower and more direct: **is `submitGfxFrame` actually being called 1152+ times as `cinematicLoopBody`'s
loop count implies, and if so, why does `[vi-fs-decision]`'s `pairs` counter stay at 0 the whole time?**

`HYPOTHESIS-ID: m5-audio-destub-submitgfxframe-vi-fs-decoupling` (new, 1st iteration).

## The work unit

1. **Source-read first, per every session's convention in this arc** (do NOT soak before this):
   - Read `submitGfxFrame`'s full body (find it via `grep -rn "submitGfxFrame" RecompiledFuncs/*.c`
     in `/Users/williambuckley/Documents/Tools/N64Recomp` — it's called from `cinematicLoopBody`
     at `funcs_27.c:108253`, per s336; find its definition and read it in full).
   - Find what `submitGfxFrame` writes to: does it enqueue a graphics task the same way
     `runVideoFrameTick`'s real producer path does (`lib/rt64/src/hle/rt64_state.cpp:2945`,
     `ultramodern/src/events.cpp:576-592`, per s330's trace), or via a completely different path?
   - Find what `[vi-fs-decision]`'s `pairs` counter actually counts (grep `rt64_state.cpp` /
     wherever `[vi-fs-decision]` is logged from — likely native C++ runtime code, not
     `fixup_game_funcs.py` patch territory, per s313/s315's precedent of finding relevant logic
     outside the game-code patch file). Does `submitGfxFrame`'s output route through whatever
     produces a "pair," or does it use some other mechanism the pairing logic doesn't recognize?
   - **Discriminating question this read should answer**: does `submitGfxFrame`'s call path
     plausibly reach the same graphics-task queue `[vi-fs-decision]` is monitoring? If yes, the
     mystery deepens (calls should produce pairs but don't — needs a runtime instrument next). If
     no — if `submitGfxFrame` writes to some other buffer/mechanism entirely — that may fully
     explain `pairs=0` without needing a new soak (same pattern as s335/s336's source-only closes).
2. If the source-read doesn't fully resolve it, instrument (batch every counter in one soak, per the
   iron rule): an entry/call counter on `submitGfxFrame` itself, plus whatever field/counter its body
   writes to that should influence `[vi-fs-decision]`'s `pairs` value. Reuse
   `ROGUESQ_LOG_CUTSCENETIMER_REACH`'s naming convention or open a new var
   (`ROGUESQ_LOG_SUBMITGFXFRAME_REACH=1`) — always `lambda m: (...)` for `re.subn` replacements.
3. Same soak setup as every session in this arc if a new soak is needed: gate narrowed to reverse
   `reapplyDisplayMode`'s site only (`0x8008E(?:B40|C88)` -> `0x8008EB40`-only),
   `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, `env HOLD_S=600 <VARS> zsh
   scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required, project rule 10).
   Positive control: confirm new counters fire early before trusting a late "stuck" reading.
4. Whichever outcome, close it in the same iteration — this is the 1st of up to 3 iterations on the
   new `HYPOTHESIS-ID`.
5. Revert to the full force-zero baseline (`audio gate patched x2`) and rebuild clean before ending.

## Maintenance flag

`docs/CURRENT-TRUTH.md` is now ~61.8 KB (over the 60,000-byte Step-0 trigger) after this session's
item -194 addition. **The next iteration is a MAINTENANCE iteration per ITERATION.md Step 0** — compact
before picking up the submitGfxFrame work unit above. Good compaction targets: items -160..-193 (the
26-session M5 gate-byte-reversal arc, s297-336) are prime candidates to fold into 2-3 paragraphs the
way s330/s336 already partially did; the "Overturned conclusions" and "Dead ends" sections are stable
and lower-value to touch.

## Environment notes (carried forward — see s327-337 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=600 <VARS> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (the `env` prefix
  is required — see project rule 10, a bare `VAR=1 zsh ...` is denied by the permission
  prefix-matcher). Run it via Bash `run_in_background: true`. Get the PID from the launch output
  (`pid <PID> out=...`), then block in a SEPARATE foreground Bash call polling `os.kill(pid, 0)` or
  `while kill -0 <PID> 2>/dev/null; do sleep 5; done` with a timeout comfortably over 600s. Log lands
  at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly (past logs have run
  tens of MB / over a million lines).
- **Existing logs are reusable evidence** — s335, s336, and s337 (partially) all answered questions by
  re-reading source or re-grepping already-captured logs instead of always re-running a soak. Check
  `scratch/s73_post_a_scene/s337cutscenetimer/run.log` for a relevant counter before spending a new
  build-run cycle, though note it doesn't have any `submitGfxFrame`-specific counter armed, so this
  question will likely need a new soak once the source-read narrows what to instrument.
- Multiple Bash calls this session hit compound-command approval friction (`cd x && cmd`,
  `VAR=1 cmd 2>&1 | tail`, etc.) — safest pattern is a standalone `cd <dir>` as its own Bash call
  (working directory persists across calls), then the actual command as a separate call with an
  absolute path where needed.
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build <path> -j8` — allowlisted
  verbatim.
- Scratch files outside the three allowed working directories (e.g. `/tmp/...`) are blocked by the
  sandbox — write throwaway analysis scripts under `scratch/` in this repo instead.

HYPOTHESIS-ID: m5-audio-destub-submitgfxframe-vi-fs-decoupling (new, 1st iteration — pivoted from
m5-audio-destub-cinematicloopbody-divergent-callees, which s337 closed at its 3-iteration budget).
