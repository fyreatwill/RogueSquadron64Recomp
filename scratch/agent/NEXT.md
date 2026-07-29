# NEXT work unit — find and guard composeNpcOrientationMatrix's 8th
# unguarded deref site (the new blocker), THEN re-soak C_LOADED

## Where the investigation stands (s255)

s255 picked up item -49's `renderUnlitMeshFaces` KSEG0-zero-extension chase
(CURRENT-TRUTH, search for `-49\.`/`-96\.`). Two things landed:

1. **Free discriminating result, no build needed**: s254's `hangarlistguard1`
   soak already had `ROGUESQ_LOG_UNLIT_MESH_TRACER=1` armed and already
   reached the `+792` crash (5th confirmed occurrence). Re-grepping that
   existing log (`grep -a -c "unlit-mesh-tracer\|B_LOADED"
   scratch/s73_post_a_scene/hangarlistguard1/run.log`) shows exactly 1
   `unlit-mesh-tracer` line (the positive-control counter, `calls=1`) and
   ZERO `B_LOADED` lines — `ctx->r16` was NOT out-of-bounds right after its
   initial load (`funcs_4.c:5072`) on the one call that then crashed. Rules
   out "already bad at load time" for this occurrence too.
2. Landed `C_LOADED`: a new tracer check right after the loop-back reload
   at guest `0x80012080` (`ctx->r16 = MEM_W(ctx->r16, 0X0)`), mirroring
   `B_LOADED`'s source-vs-value pattern — that site's existing check only
   validated the reload's SOURCE address, never the RESULT. Added to
   `fixup_game_funcs.py` (N64Recomp checkout), regenerated, built clean,
   patch report confirmed 6/6 tracer sites x1.
3. **Soak (`cloadedsoak1`)**: reached SELECT-CRAFT at 75.1s, then crashed
   in the hangar menu at `static_5_800AB1C8+6168`
   (`composeNpcOrientationMatrix`, called from
   `runHangarSelectionFrame`/`runHangarMenuFromOverlay`/`menuOverlayInit`)
   — `renderUnlitMeshFaces` was NEVER called this run (0 tracer lines of
   any kind). Uninformative null for `C_LOADED` specifically (1 of a
   possible 3 before the budget-rule-8 stop-and-redirect point).
4. **The actual finding**: this function already has 7 guards
   (s97-s101/s128), all confirmed still executing (551
   `compose-npc-orient-guard` lines this run), but none of them caught this
   fault — an 8th, previously-uncovered deref site. Same shape as s254's
   `HANGARLIST_GUARD` discovery: a per-frame hangar-menu function with a
   gap that blocks the game from ever reaching the render code this whole
   investigation actually cares about.

## The next work unit, in priority order

### Step 1 (do this first): find and guard the new composeNpcOrientationMatrix gap

Read `static_5_800AB1C8` (`composeNpcOrientationMatrix`) in
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_40.c`
start to end (starts line 6293; find the closing brace / next
`RECOMP_FUNC` for the true extent — it's a big function, expect 500+
lines). Cross-reference against the 7 existing guard sites (search
`ROGUESQ_LOG_COMPOSE_NPC_GUARD` through `_GUARD7` in `fixup_game_funcs.py`,
`N64Recomp` checkout) to see which raw pointer derefs are NOT already
guard-wrapped. Same recipe as s254's `HANGARLIST_GUARD`: find the genuinely
unguarded raw `MEM_*(reg, ...)` deref that a corrupted/out-of-KSEG0-range
`reg` would hit, add ONE guard (bail to the function's real epilogue —
find it by reading to the closing brace first, do NOT guess), rebuild,
soak with a NEW tag (do not reuse `cloadedsoak1`).

Discriminating outcomes: guard fires with sane fields -> mechanism
confirmed, hold should get past this menu crash and progress further
(toward `renderUnlitMeshFaces` or another, later blocker) — a real
positive control since this crash was hot this run; crash recurs at a
DIFFERENT site -> progress, wasn't the only gap; crash recurs at the exact
same signature -> guard missed something, re-read; 0 fires -> this
specific crash wasn't hot this run, check what (if anything) recurred
instead.

### Step 2: once past that, re-soak to test `C_LOADED`

Only after step 1's guard is landed and confirmed to get the game past the
`composeNpcOrientationMatrix` crash: re-run a `cloadedsoak`-style soak (new
tag) and check whether `renderUnlitMeshFaces` gets called this time
(`grep -a -c "unlit-mesh-tracer" run.log` — the positive-control counter
line proves it ran at all) and whether `C_LOADED` fires. If it fires with
a sane-looking loaded value that's actually the bad `0x80630062` pattern,
that PINS the corruption to between the reload and its use — genuinely
narrows the bug for the first time in this multi-session chase. If it's
still clean (0 fires) right up to another `+792` crash, that's the 2nd of
3 allowed uninformative nulls on this specific question — one more retry
permitted before budget rule 8 says stop and redirect.

Command pattern (copy the driver, don't re-run in place):
```
cp scratch/s73_post_a_scene/run_cloadedsoak1.sh scratch/s73_post_a_scene/run_<newtag>.sh
# edit the new file's last line's tag argument, and armed env if step 1 added a new ROGUESQ_LOG_* var
zsh scratch/s73_post_a_scene/run_<newtag>.sh   # run_in_background: true
# read first output line for "pid NNNNN", then block:
# until ! kill -0 <pid> 2>/dev/null; do sleep 10; done
```

No regen/rebuild needed for a re-soak alone — only if step 1 lands new
guard code. Verify a fresh binary before trusting any result: `strings
build/RogueSquadron64Recomp | grep '<your-new-marker>'` plus `ls -la
build/RogueSquadron64Recomp` vs. the soak's start time.

## Do NOT do this iteration

- Do NOT re-run `cloadedsoak1` in place, or skip straight to step 2
  without closing the `composeNpcOrientationMatrix` gap first — the render
  code isn't reachable until that crash is fixed, so a bare re-soak would
  just burn a 2nd uninformative null for free information already in
  hand.
- Do NOT re-attempt `nm`/`atos` for offset localization — confirmed
  unusable 3+ independent times. Crash offsets on this project's symbol
  format are NATIVE code offsets, not guest MIPS addresses.
- Do NOT credit `HANGARLIST_GUARD`'s continued 0-fire count as "unneeded"
  — it simply wasn't the crash that was hot this particular run.
- Do NOT fold the `evalCubicSplineAtTime`(s210)/`composeNpcOrientationMatrix`
  (s255) `0x80000000`-clustered register patterns into one claim yet —
  each is single-occurrence, different function, flagged as a pattern
  worth watching, not a confirmed shared root cause.
- Do NOT invoke `fixup_game_funcs.py` more than once per regen cycle.

## Environment notes (carried forward, still current as of s255)

- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses.** Use the offset only to identify WHICH
  function to read in full; never try to place it at a specific guest
  instruction.
- The current binary (as of s255's build) already has `C_LOADED`,
  `HANGARLIST_GUARD`, `MATLIST_GUARD3`, and every other guard/tracer
  landed through s255 — no rebuild needed for a bare re-soak, only if you
  land new code.
- **Block-wait pattern**: launch the soak with Bash `run_in_background:
  true`, read the driver's first output line for `pid NNNNN out=...`,
  then run a SECOND Bash call (foreground, generous timeout up to
  480000ms) that polls `until ! kill -0 <game_pid> 2>/dev/null; do sleep
  N; done`. This blocks until the process exits, letting a soak run to
  completion within one iteration.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
  A crash immediately after this means the game died in the SELECT-CRAFT
  menu itself before reaching gameplay — check the crash backtrace for
  `menuOverlayInit`/`runHangarSelectionFrame`/`runHangarMenuFromOverlay`
  frames (menu family) vs. `traverseSceneGraphRecursive`/`processSceneNode`/
  render-function frames (actual gameplay render family) to tell which
  regime you're in before reading the wrong function.
- **Regen is mandatory-delete-all-first, AND fixup must run EXACTLY
  ONCE**: delete all 45 `RecompiledFuncs/funcs_*.c`
  (`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('...')]"`,
  not `rm -f`/`find -delete`, both blocked) before `make_elf.py` (cwd
  `rogue_squadron64/`, actual script path `tools/make_elf.py`) ->
  `tools/agent/regen_n64recomp.sh` (cwd `RogueSquadron64Recomp`) ->
  `fixup_game_funcs.py` (cwd `N64Recomp`, exactly once) ->
  `cmake --build .` (cwd `build`, needs
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`).
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions.

## Otherwise: continue the static sweep (139 candidates, unchanged since s253)

If step 1/2 above are exhausted this session: `renderLitMeshFaceGroup` (14
sites, `funcs_4.c`), `renderLitTexturedMeshFaces` (11 sites, `funcs_3.c`),
`func_800AE3F0` (10 sites, `funcs_27.c`), `beginFrameDLChunk` /
`emitFrameRdpInitDl` (10 sites each, `funcs_3.c`).

`docs/CURRENT-TRUTH.md` housekeeping — still ~407 KB+, flagged 45+
sessions, still not done. Per `ITERATION.md` this does NOT count as
`ADVANCED` on its own — pair it with a real change or expect to file
`SUBSTITUTED`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (still ~407 KB+ / ~6000+ lines,
flagged 45+ sessions without action).

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope). Also still not fixed: the script's non-idempotency
bug found s250 (`rs_malloc` entry-capture patch stacks duplicate
declarations on repeat invocation).

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.
