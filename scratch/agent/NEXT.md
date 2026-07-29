# NEXT work unit — guard the unguarded pointer feeding `evalCubicSplineAtTime`'s
# Bus error (s258 lead, a NEW crash site reached deeper into the same
# `static_5_800AB658` menu-crash whack-a-mole family)

## Where the investigation stands (s258)

s258 closed the 2 gaps its own scan found in `static_5_800AB658`'s
already-systematic `-0x25A4` array-deref guard family (`fixup_game_funcs.py`'s
`_hangarbay_deref_guard_sites`, s132): 26 sites (G1-G29) were guarded as of
s132's "complete" audit, but a fresh full-body read (prompted by s257's
own crash) found 2 more identical-shape occurrences the original sweep
missed, between `G28` (`0x800ADA2C`) and the `G29` merge point
(`L_800ADB18`): `0x800ADA88`/`0x800ADAD4` (funcs_40.c:14302-14305,
14348-14351). Added as `G30`/`G31`, same guard generator, same env var
(`ROGUESQ_LOG_HANGAR_BAY_DEREF_GUARD`), same exit label. Full regen,
clean build, `strings`-verified (28 `hangar-bay-deref-guard` literals,
up from 26).

**Soak (`g30g31soak1`, `scratch/s73_post_a_scene/g30g31soak1/run.log`,
~212MB): G30/G31 got 0 fires (uninformative null on that exact
question), but the run crashed at a NEW, deeper site — real evidence of
progress even without a fire.** The SELECT-CRAFT phase transition landed
at the usual 74.9s (`update_screen #4460`). s257's run crashed almost
immediately after (`#4474`, ~14 ticks later). **This run survived to
`update_screen #8320` — roughly 3860 more VI updates** — before crashing,
still inside the same outer call chain (`mainGameLoop` ← `menuOverlayInit`
← `runHangarMenuFromOverlay` ← `runHangarSelectionFrame` ←
`static_5_800AB658`), but this time at native offset **+61812** (not
s257's +49104), reached through a subroutine chain never before
implicated in this bug family:

```
static_5_800AB658 (+61812)
  -> setupActorAnchorTransformType1 (+368)
    -> buildPositionAndCallTransformHelper (+1292)
      -> evalCubicSplineAtTime (+732, CRASHES at +1008)
```

Register dump: `pc=0x104e5c5a8`, `far=0x37ffffff8`, `x8=0x0000000300000000`
(rdram host base), `x9=0x000000007ffffff8` (the wild guest-side value —
note this is NOT the familiar `0x80630062`-shaped KSEG0-zero-extension
value seen in item -49's occurrences; it looks more like a raw
`0x7FFFFFF8`-ish sentinel or a corrupted/uninitialized float-adjacent
value — read the crash site itself before assuming it's the same
mechanism as item -49). Bus error (signal 10), not segfault — consistent
with a misaligned or wildly-out-of-range access.

**Caveat, carried forward honestly**: this was a single run, not a
formal same-run A/B (iron rule 2 forbids cross-run A/B on animating
menu/scene state anyway). The ~4x-longer survival is *suggestive* that
closing G30/G31 helped, but it is equally possible this is scripted-
input run-to-run variance reaching a slightly different code path.
Treat as single-source (iron rule 4) until a second independent line of
evidence agrees (e.g. two more soaks both surviving similarly long).

`unlit-mesh-tracer` again had 0 hits this run (`renderUnlitMeshFaces`
still never called) — the game is still dying in the hangar menu before
ever reaching gameplay rendering, so `R7A_LOADED`/`R7B_LOADED` (item -49's
open sub-question) still have not had a positive-control opportunity.
Do NOT re-attempt that soak until this NEW blocker is also closed.

## The next work unit, in priority order

### Step 1: read `evalCubicSplineAtTime`, `buildPositionAndCallTransformHelper`,
### `setupActorAnchorTransformType1` for the unguarded pointer

```
grep -n "^RECOMP_FUNC.*evalCubicSplineAtTime\|^RECOMP_FUNC.*buildPositionAndCallTransformHelper\|^RECOMP_FUNC.*setupActorAnchorTransformType1" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
```

`evalCubicSplineAtTime` already has an existing div-by-zero guard
(unrelated — from an earlier session, see fixup report line
"evalCubicSplineAtTime div0 guard patched x1"); do not confuse that with
what's needed here. We need a pointer-range guard, same idiom as every
prior guard in this project (`RENDERUNLIT_GUARD` in funcs_4.c:5044-5060
is still the canonical example to copy). Since these are 3 small-ish
functions (not a 7000-line function like `static_5_800AB658`), a single
read of each in full should be tractable without fanning out multiple
agents — try reading each function directly first; only fan out if one
of them turns out to be unexpectedly large.

Look for a `MEM_W`/`MEM_H`/`MEM_B`-loaded value used as a base pointer
with no `0x80000000`-`0x80800000` + `0xFFFFFFFF`-hi-word range check
before the dereference — the crash's `x9=0x7ffffff8` value is notably
NOT in the `0x80000000-0x80800000` range itself (it's below it), so the
existing guard idiom's bounds check should catch it cleanly if applied
at the right site.

### Step 2: guard the earliest unvalidated load found, same idiom as always

Copy the `RENDERUNLIT_GUARD`-style block (range-check + zero-and-bail on
failure, respecting the function's own control flow for where "bail"
should jump to — read enough context to find the right target, don't
invent one).

### Step 3: full regen -> build -> soak (new tag)

```
cd /Users/williambuckley/Documents/Tools/rogue_squadron64
python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"
python3 tools/make_elf.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
zsh tools/agent/regen_n64recomp.sh
cd /Users/williambuckley/Documents/Tools/N64Recomp
python3 fixup_game_funcs.py   # exactly once -- confirm your new guard's report line appears
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build .
strings /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build/RogueSquadron64Recomp | grep <new guard's env-var name>
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene
cp run_g30g31soak1.sh run_<newtag>.sh   # edit the last line's tag; ROGUESQ_LOG_HANGAR_BAY_DEREF_GUARD stays armed as a same-run control, add your new guard's env var too
zsh run_<newtag>.sh   # run_in_background: true, then block-wait on the pid
```

Block-wait pattern: read the driver's first output line for `pid NNNNN`,
then a SECOND foreground Bash call (timeout up to 480000ms):
`until ! kill -0 <pid> 2>/dev/null; do sleep 10; done`.

**Discriminating outcomes**: new guard fires with sane fields -> real
mechanism found; if the hold now survives further AND
`renderUnlitMeshFaces` finally gets called (`unlit-mesh-tracer` positive
control fires), R7A/R7B_LOADED get their first real test in the same
run — read their fire counts directly. Crash recurs at a DIFFERENT site
-> still progress, repeat the process. Crash recurs at the EXACT same
`evalCubicSplineAtTime`/`buildPositionAndCallTransformHelper`/
`setupActorAnchorTransformType1` signature -> guard missed the actual
load or didn't cover all call paths into these functions (they may be
called from elsewhere too — grep for other callers before assuming
`static_5_800AB658` is the only entry point).

## Do NOT do this iteration

- Do NOT re-run `g30g31soak1` in place — copy to a new tag.
- Do NOT credit G30/G31 with fixing anything beyond "matches the
  established idiom, 0 fires so far" — the survival-length improvement
  is single-source evidence, not confirmed causality (see caveat above).
- Do NOT re-attempt the R7A/R7B_LOADED soak until this NEW
  `evalCubicSplineAtTime` blocker is closed — the game still never
  reaches `renderUnlitMeshFaces`.
- Do NOT re-attempt `nm`/`atos`/`objdump` for offset localization --
  confirmed unusable 3+ independent times. Use `scratch/agent/machoparse.py`
  if function-size verification is ever needed again.
- Do NOT skip straight to guarding without reading the function bodies
  first — same rule as every prior guard in this file.

## Environment notes (carried forward, still current as of s258)

- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses.** Use the offset only to identify WHICH
  function to read in full; never try to place it at a specific guest
  instruction or extrapolate C line number from it.
- **Block-wait pattern**: launch the soak with Bash `run_in_background:
  true`, read the driver's first output line for `pid NNNNN out=...`,
  then a SECOND Bash call (foreground, timeout up to 480000ms) that polls
  `until ! kill -0 <game_pid> 2>/dev/null; do sleep N; done`.
- `/tmp` is not writable this session — write scratch/report files inside
  `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`. Compound
  `cd ... && ... > file` commands with output redirection after a `cd`
  get blocked for approval — run `cd` as its own Bash call first (cwd
  persists across calls in this harness), then run the next command with
  no `&&`/redirect chaining, or use absolute paths and skip `cd`
  entirely. Same for bare `git -C <path> ...` and `git status` chained
  after a `cd` — prefer a plain `cd <path>` call first, then a bare
  `git status`/`git ...` with no `-C` and no chaining.
- Redirecting a build/regen command's output to a scratch log file with
  `> path 2>&1` on the SAME line as the command can itself get rejected
  (seen s258: `python3 tools/make_elf.py > log 2>&1` failed with a
  cryptic "Contains simple_expansion" error even with no `cd` in the
  command) — if that happens, just run the bare command without
  redirection and let the tool's own output capture handle it; don't
  burn time debugging the redirect.
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
  Use `update_screen #N` counts before/after this line to measure how far
  a run got, in lieu of wall-clock (wall-clock varies run to run; VI tick
  count is a more stable proxy for "how far into the menu did it get").
- **Regen is mandatory-delete-all-first, AND fixup must run EXACTLY
  ONCE**: delete all 45 `RecompiledFuncs/funcs_*.c`
  (`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('...')]"`,
  not `rm -f`/`find -delete`, both blocked) before `make_elf.py` (cwd
  `rogue_squadron64/`, actual script path `tools/make_elf.py`) ->
  `tools/agent/regen_n64recomp.sh` (cwd `RogueSquadron64Recomp`) ->
  `fixup_game_funcs.py` (cwd/path in `N64Recomp`, exactly once) ->
  `cmake --build .` (cwd `build`, needs
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`).
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions.
- `fixup_game_funcs.py` lives ONLY in the untracked sibling `N64Recomp`
  checkout (not a git submodule of this repo) — edits there are real and
  necessary for every guard, but are NOT part of this repo's commit
  scope (flagged since s83, still the user's call).
- **A big full-body sweep declaring itself "complete" is not a
  guarantee** (s132 said "26/26, audit series complete" and was still
  missing 2 sites, found by s257/s258). If a future session's own read of
  a "fully guarded" family's address range turns up an anomaly, trust
  the fresh read over the old completeness claim.

## Otherwise: continue the static sweep (139 candidates, unchanged since s253)

If step 1-3 above are exhausted this session: `renderLitMeshFaceGroup` (14
sites, `funcs_4.c`), `renderLitTexturedMeshFaces` (11 sites, `funcs_3.c`),
`func_800AE3F0` (10 sites, `funcs_27.c`), `beginFrameDLChunk` /
`emitFrameRdpInitDl` (10 sites each, `funcs_3.c`).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (still ~432 KB+ / ~6200+ lines,
flagged 48+ sessions without action). Its top-of-file "as of session 166"
header is also stale (actual session count is 258+) — nobody has
corrected this drift in a long time; flagging again, still not this
session's focus.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope). Also still not fixed: the script's non-idempotency
bug found s250 (`rs_malloc` entry-capture patch stacks duplicate
declarations on repeat invocation).

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.
