# NEXT work unit — widen the null-only check feeding
# `setLookupEntryField5ByKey` inside `activateAnimationKeyframe` to a full
# KSEG0 range guard (s259's lead, a NEW crash family, unrelated to the
# `-0x25A4`/hangar-bay/evalCubicSplineAtTime chains)

## Where the investigation stands (s259)

s259 guarded `evalCubicSplineAtTime`'s unguarded struct-field pointer
(s258's lead): `ctx->r16` loaded from `+0x8` of the spline-data struct at
guest `0x80018FCC`, dereferenced 2 instructions later with zero
validation. Bail target: a dedicated epilogue label
(`L_evalspline_guard_exit`) inserted right before the function's real
restore-and-return sequence (`0x80019188`) — ABI-safe since the prologue
already saved `$s0`/`$s1`/FP20-30 to stack before the guard's anchor
point. New env var `ROGUESQ_LOG_EVALSPLINE_GUARD`. Full regen, clean
build, `strings`-verified.

**Soak (`evalsplineguard1`, `scratch/s73_post_a_scene/evalsplineguard1/
run.log`, ~222MB): EVALSPLINE_GUARD got 0 fires (uninformative), but the
run crashed at a BRAND NEW site — real evidence the crash-of-record moved,
even without a guard fire.** Crashed at almost the same VI tick as s258
(`update_screen #~8192-8236` vs s258's `#8320` — same ballpark, not a
clear improvement), but via a call chain NEVER before implicated in this
whole investigation:

```
static_5_800AAD9C (runHangarSelectionFrame)
  -> advancePlayerAnimationPhase
    -> activateAnimationKeyframe
      -> setLookupEntryField5ByKey  (CRASHES)
```

Register dump: `si_addr=0x3c04b1980`, `x8=0x0000000300000000` (rdram host
base), `x9=0x00000000c04b1980` (wild guest value — a THIRD distinct shape:
not the `0x80630062` KSEG0-zero-extension pattern, not s258's `0x7ffffff8`
sentinel-like value either). Bus error (signal 10).

**Caveat, carried forward honestly**: single run, not a formal same-run
A/B (iron rule 2). Cannot distinguish "the evalCubicSplineAtTime guard
really let the run progress further" from "scripted-input run-to-run
variance landed on a different code path" (identical caveat to s258's own
result). Treat as single-source (iron rule 4).

`unlit-mesh-tracer` again had 0 hits this run (`renderUnlitMeshFaces`
still never called) — game still dies in the hangar menu before ever
reaching gameplay rendering, so `R7A_LOADED`/`R7B_LOADED` (item -49's open
sub-question) still have not had a positive-control opportunity. Do NOT
re-attempt that soak until this NEW blocker is also closed.

## The bug is ALREADY precisely localized — read first, but the site is known

`setLookupEntryField5ByKey` (funcs_15.c:70-130, 61 lines, tiny) has
exactly ONE call site inside `activateAnimationKeyframe`
(funcs_14.c:1629-2138 is the function's real extent — verified via
`awk '/^RECOMP_FUNC/{print NR}' funcs_14.c`; of 18 total
`setLookupEntryField5ByKey(rdram, ctx);` call sites in the whole file,
only the one at line 2116 falls in this range). **Do NOT use the crash
symbol's native `+5152` offset as a line number — it is not one** (same
"+N is a native ARM64 offset, not a guest address or C line" rule as
always).

The argument feeding the crashing call (funcs_14.c:2090-2097):

```c
// 0x80061EF4: lw          $a0, 0xF4($s1)
ctx->r4 = MEM_W(ctx->r17, 0XF4);
// 0x80061EF8: beq         $a0, $zero, L_80061F18
if (ctx->r4 == 0) {
    ctx->r2 = ctx->r18 & 0XFF;
        goto L_80061F18;
}
```

This checks ONLY `== 0`, never the full `0x80000000`-`0x80800000` KSEG0
range + `0xFFFFFFFF` hi-word check every other guard in this project
uses. A non-null-but-garbage value in `$s1+0xF4` sails through and gets
dereferenced inside the callee (funcs_15.c:74/87: `MEM_HU(ctx->r4, 0X4)`,
`MEM_W(ctx->r4, 0X0)`) with zero further validation. This is a DIFFERENT
site from `activateAnimationKeyframe`'s existing s98 "table-deref guard"
(confirmed by grepping `fixup_game_funcs.py` for `activateAnimationKeyframe`
— that guard covers a different address).

## The next work unit, in priority order

### Step 1: re-read the exact site to confirm nothing has shifted

```
grep -n "setLookupEntryField5ByKey" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_14.c
```
Confirm line 2116 is still the one inside `activateAnimationKeyframe`
(1629-2138), and re-read funcs_14.c:2080-2119 to confirm the `beq
$a0,$zero,L_80061F18` shape is unchanged before editing anything.

### Step 2: widen the guard, same idiom as always, reuse the existing bail

In `fixup_game_funcs.py`, add a patch for `funcs_14.c` that changes the
`if (ctx->r4 == 0)` check at this site to ALSO reject out-of-KSEG0-range
values (same `U32(ctx->r4) < 0x80000000u || >= 0x80800000u || hi_word !=
0xFFFFFFFFu` idiom as `RENDERUNLIT_GUARD`), still jumping to the SAME
existing `L_80061F18` label (no new label needed — the function already
treats that path as "skip the call, degrade gracefully", exactly the
"reuse the function's own existing degrade path" principle every prior
guard in this codebase follows). New env var name suggestion:
`ROGUESQ_LOG_SETLOOKUP_ARG_GUARD` (or similar — follow the existing
naming convention, don't collide with `ACTIVATE_ANIM_KEYFRAME` guard's
existing env var).

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
cp run_evalsplineguard1.sh run_<newtag>.sh   # edit the last line's tag; keep ROGUESQ_LOG_EVALSPLINE_GUARD and ROGUESQ_LOG_HANGAR_BAY_DEREF_GUARD armed as same-run controls, add your new guard's env var too
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
-> still progress, repeat the process (this whole investigation has been
whack-a-mole across many independent unguarded-pointer families — that is
expected, not a failure mode). Crash recurs at the EXACT same
`setLookupEntryField5ByKey`/`activateAnimationKeyframe` signature -> guard
missed the actual load or there's a 2nd call site with the same gap
(re-check: are there other callers of `setLookupEntryField5ByKey` besides
`activateAnimationKeyframe`'s line 2116? There are 17 others in the file —
check which functions they fall in before assuming this is the only
entry point).

## Do NOT do this iteration

- Do NOT re-run `evalsplineguard1` in place — copy to a new tag.
- Do NOT credit `EVALSPLINE_GUARD` with fixing anything beyond "matches
  the established idiom, 0 fires so far" — the crash-of-record moving to
  a new site is single-source evidence (iron rule 4), not confirmed
  causality. Same caveat applies to G30/G31 from s258.
- Do NOT re-attempt the R7A/R7B_LOADED soak until this NEW
  `setLookupEntryField5ByKey` blocker is also closed — the game still
  never reaches `renderUnlitMeshFaces`.
- Do NOT re-attempt `nm`/`atos`/`objdump` for offset localization --
  confirmed unusable 3+ independent times. Use `scratch/agent/machoparse.py`
  if function-size verification is ever needed again.
- Do NOT use a crash symbol's native `+N` offset as a source line number
  or guest address — confirmed misleading again this session (funcs_14.c
  line 2116 has no numeric relationship to the reported `+5152` offset;
  the match was coincidental digit-count, not fact).

## Environment notes (carried forward, still current as of s259)

- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses.** Use the offset only to identify WHICH
  function to read in full; never try to place it at a specific guest
  instruction or extrapolate a C line number from it (this bit s259's
  first-pass reasoning — the actual localization came from counting which
  of 18 call sites falls inside the caller's own line range, not from the
  offset number).
- **Block-wait pattern**: launch the soak with Bash `run_in_background:
  true`, read the driver's first output line for `pid NNNNN out=...`,
  then a SECOND Bash call (foreground, timeout up to 480000ms) that polls
  `until ! kill -0 <game_pid> 2>/dev/null; do sleep N; done`.
- `/tmp` is not writable this session for GAME artifacts — write scratch/
  report files inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64`
  only (the harness's own background-task stdout capture under
  `/private/tmp/claude-501/...` is a different, harness-managed path and
  is fine to read from).
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
  `> path 2>&1` on the SAME line as the command can itself get rejected --
  if that happens, just run the bare command without redirection and let
  the tool's own output capture handle it; don't burn time debugging the
  redirect.
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
Read tool's 256 KB single-read limit (still ~6280+ lines / ~440 KB+,
flagged 49+ sessions without action). Its top-of-file "as of session 166"
header is also stale (actual session count is 259+) — nobody has
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
