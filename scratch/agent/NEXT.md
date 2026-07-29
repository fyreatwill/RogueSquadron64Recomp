# NEXT work unit — pick up the renderUnlitMeshFaces KSEG0-zero-extension
# tracer (item -49), OR keep re-soaking to confirm heapwalker-guard4/
# MATLIST_GUARD3 ever fire now that a run gets past the hangar menu

## Where the investigation stands (s254)

s254 re-ran s253's prescribed re-soak (`matlistguard3soak2`) and got a
real discriminating answer: `MATLIST_GUARD3`/`heapwalker-guard4` still
didn't fire, but this time the run crashed almost immediately after
SELECT-CRAFT (hold-iter 1, wall=0s) at a NEW site inside the hangar-
selection MENU itself (`static_5_800A9270`, called from
`runHangarSelectionFrame`/`runHangarMenuFromOverlay`/`menuOverlayInit`)
— **this explains why those two controls never fire**: the game dies in
the menu before ever reaching the render code that would exercise them.

Full detail: PORTING-STATE Session 254. Landed:

1. Full start-to-end read of `static_5_800A9270` (funcs_40.c:5314-5463)
   found a genuine, previously-unguarded gap: a fixed-table-indexed
   linked-list-insert idiom loads a pointer `p` (`ctx->r3 = MEM_W(ctx->r4,
   0X4)` at `0x800A92FC`) with ZERO validation, then dereferences it 3x
   with no null/range check anywhere in the function — same
   hangar-selection per-frame family as the already-catalogued 9th-17th
   crash classes (PORTING-STATE s89-s110), but this exact site was never
   guarded before (prior guards here, s101/s128, only cover the
   `projectModelBoundsToScreen` callee this function calls).
2. Added `HANGARLIST_GUARD` (`fixup_game_funcs.py`, sibling `N64Recomp`
   checkout), 1 site, right after the first load, before any of the 3
   uses. Bails to the real epilogue `L_800A9350` (confirmed by reading to
   the closing brace) on invalid/null. New env var
   `ROGUESQ_LOG_HANGARLIST_GUARD`.
3. Build clean, patch report confirmed `funcs_40.c: static_5_800A9270
   hangar-select list-insert guard (HANGARLIST_GUARD) patched x1`, no
   stacking. Binary verified fresh (`strings` shows `hangarlist-guard` x1
   and `scene-matlist-guard3` x2, mtime after build).
4. **Soak** (`hangarlistguard1`): `HANGARLIST_GUARD` fired 0/1 (not
   exercised this run), but the run got PAST the menu crash entirely —
   sustained render-loop activity (`campose-entry` 238x, `scene-rq-
   counter-hb` 115x, `present-1024` 1918x, `rs-malloc-walk`/`rs-free-walk`
   in the millions) that `matlistguard3soak2` never reached (0 renders,
   dead in the menu at hold-iter 1). **Hold survived to hold-iter 27
   (wall=30s) — a 27x improvement** over the immediately-prior run under
   an otherwise-identical script/schedule/binary-family, before crashing
   to a DIFFERENT bug.
5. That next crash is NOT new: `renderUnlitMeshFaces+792`,
   `si_addr=0x380630062` — an EXACT match (same offset, same faulting
   value) to s208's `unlitmeshtracer3` occurrence. This is the **5th**
   confirmed occurrence of CURRENT-TRUTH item -49's long-tracked, not-
   yet-root-caused "KSEG0-zero-extension" bug (a deterministic,
   non-random data source per s208's own reasoning) — genuinely
   different in kind from this session's own `HANGARLIST_GUARD`-shaped
   gaps (item -49 already ruled out "source register bad at load time"
   for the two nearest sites; needs the wider tracer it prescribes, not
   another guard-by-inspection).
6. Ran item -49's own cheapest prescribed step (no build needed): grepped
   `rogue_squadron64/symbol_files/*.txt` for the literal `80630062` — 0
   hits. Rules out "the recurring value is a named symbol/asset address"
   as an explanation.

## Two live options, in priority order

### Option A (recommended first): pick up item -49's own next step

This is a SEPARATE, already-well-defined investigation with its own
history (s194-s210+), not a "read the function, add a guard" job like
this session's fix. CURRENT-TRUTH item -49 (search
`docs/CURRENT-TRUTH.md` for `-49\.`) prescribes: widen the existing
`unlitmeshtracer` tracer to check `ctx->r16` itself (not just its load's
source address) right after `funcs_4.c` line ~5029's site-B load, before
line 5057's first subsequent dereference — `ctx->r16` is dereferenced
~35 more times before the loop-back reload (5057, 5069, 5114-5195,
5347-5542) and none of those are currently checked. Read the whole
tracer-building history in item -49/-48 before starting (PORTING-STATE
Session 206-210) so you don't rebuild something that already exists.
Discriminating outcome: if the widened tracer catches `ctx->r16` already
holding `0x0000000080630062` at some point BEFORE the crash, that
narrows the bug to wherever it first got that value (upstream of this
function entirely); if it's still clean right up to the fault, the bug
is even more exotic than currently framed (re-open hypothesis (b),
ARM64 codegen, last resort per boring-first).

### Option B: another re-soak to check heapwalker-guard4/MATLIST_GUARD3

Now that a run can get past the hangar menu (with `HANGARLIST_GUARD`
armed), re-run `hangarlistguard1`-equivalent env (new tag) and see
whether the hold gets far enough this time to exercise
`heapwalker-guard4`/`MATLIST_GUARD3` before hitting the
`renderUnlitMeshFaces` bug again — if `renderUnlitMeshFaces` crashes
every time before those controls get a chance to fire, that's useful
information for prioritizing Option A over more matlist re-soaking (the
render bug is now the actual bottleneck for testing those two guards,
not anything wrong with them). Do NOT do this a 3rd consecutive time
without a discriminating result per `ITERATION.md` rule 8 — if this soak
also just hits `renderUnlitMeshFaces` again with no new information,
that's your signal to switch to Option A instead of a 4th soak.

Commands for either option's soak (copy the driver, don't re-run in
place):
```
cp scratch/s73_post_a_scene/run_hangarlistguard1.sh scratch/s73_post_a_scene/run_<newtag>.sh
# edit the new file's last line's tag argument
zsh scratch/s73_post_a_scene/run_<newtag>.sh   # run_in_background: true
# read first output line for "pid NNNNN", then poll:
# until ! kill -0 <pid> 2>/dev/null; do sleep 10; done
```
No regen/rebuild needed for a re-soak — the s254 binary already has
`HANGARLIST_GUARD` (verify with `strings build/RogueSquadron64Recomp |
grep hangarlist-guard` before trusting it).

## Otherwise: continue the static sweep (139 candidates, unchanged since s253)

If both options above are exhausted this session, fall back to the
static sweep from `scratch/agent/NEXT.md`'s s253 version (still valid):
`renderLitMeshFaceGroup` (14 sites, `funcs_4.c`, has a 10th uncounted
`findAndUnlinkSmallestEntry` occurrence at guest `0x800148BC` per s253's
finding), `renderLitTexturedMeshFaces` (11 sites, `funcs_3.c`),
`func_800AE3F0` (10 sites, `funcs_27.c`), `beginFrameDLChunk` /
`emitFrameRdpInitDl` (10 sites each, `funcs_3.c`).

`docs/CURRENT-TRUTH.md` housekeeping — still ~407 KB+, flagged 44+
sessions, still not done. Per `ITERATION.md` this does NOT count as
`ADVANCED` on its own — pair it with a real change or expect to file
`SUBSTITUTED`.

## Do NOT do this iteration

- Do NOT re-run `hangarlistguard1` or `matlistguard3soak2` in place (or
  any prior tag) — new soaks need new tags, re-running overwrites
  `run.log`.
- Do NOT re-attempt `nm`/`atos` for offset localization — confirmed
  unusable 3 independent times (s207 x2, s252). Remember crash offsets on
  this project's symbol format are NATIVE code offsets, not guest MIPS
  addresses.
- Do NOT treat `renderUnlitMeshFaces+792` as a simple missing-guard gap
  and add a guard-by-inspection fix without reading item -49's full
  history first — s204's static read of this exact function was already
  "clean" (no raw pointer arithmetic bypass found), and the bug still
  recurred dynamically; this is NOT the same shape as `HANGARLIST_GUARD`
  or the other whack-a-mole guards in this project. Read PORTING-STATE
  s194/s206-210 before touching this function again.
- Do NOT credit `HANGARLIST_GUARD`'s 0/1 fire count as "the guard is
  unneeded" — it wasn't exercised because the run this time didn't hit
  the bad-pointer condition, not because the gap doesn't exist. The
  27x-longer hold is the actual evidence the fix helped (indirectly, by
  removing a crash between the previous bottleneck and further progress).
- Do NOT invoke `fixup_game_funcs.py` more than once per regen cycle.
- Do NOT revive the NaN_CHECK-disable idea (CURRENT-TRUTH `-55`/`-56`) —
  already tried, A/B-tested, and reverted at s216 (`-57`).

## Environment notes (carried forward, still current as of s254)

- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses.** Use the offset only to identify WHICH
  function to read in full; never try to place it at a specific guest
  instruction.
- **Permission gate CONFIRMED CLEARED through s254** for the standard
  `tools/*`/`build/*`/`python3:*`/`zsh:*` command families, plus plain
  `git status`/`grep` in the sibling `rogue_squadron64`/`N64Recomp`
  checkouts. `nm`/`atos` still not allowlisted. `cd` into `lib/*`
  submodule directories requires interactive approval this session even
  for read-only `git status` — use `git -C <path>` or just avoid touching
  `lib/` when there's nothing to edit there.
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process.
- **Env-gated logging pattern**: `static const bool s_X = [](){ const
  char *v = std::getenv("VAR_NAME"); return v && v[0] && v[0] != '0'; }();`
  then `if (s_X) { std::fprintf(stderr, ...); std::fflush(stderr); }`.
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
- **`campose*`/`hangarlistguard1` armed env-var set** (unchanged since
  `campose11`, now plus `ROGUESQ_LOG_SCENE_MATLIST_GUARD3` s253 and
  `ROGUESQ_LOG_HANGARLIST_GUARD` s254): see
  `scratch/s73_post_a_scene/run_hangarlistguard1.sh` for the full current
  set (this file survives across sessions on disk even though `scratch/`
  is gitignored — copy it forward for new soaks; only
  `STATUS`/`OUTCOME`/`NEXT.md`/`run_mission_keys.sh` are git-tracked).
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
  A crash immediately after this (hold-iter 0-1) means the game died in
  the SELECT-CRAFT menu itself before reaching gameplay — check the
  crash backtrace for `menuOverlayInit`/`runHangarSelectionFrame`/
  `runHangarMenuFromOverlay` frames (menu family) vs.
  `traverseSceneGraphRecursive`/`processSceneNode`/render-function frames
  (actual gameplay render family) to tell which regime you're in before
  reading the wrong function.
- **Regen is mandatory-delete-all-first, AND fixup must run EXACTLY
  ONCE**: delete all 45 `RecompiledFuncs/funcs_*.c`
  (`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('...')]"`,
  not `rm -f`/`find -delete`, both blocked) before `make_elf.py` (cwd
  `rogue_squadron64/`, actual script path `tools/make_elf.py`) ->
  `tools/agent/regen_n64recomp.sh` (cwd `RogueSquadron64Recomp`) ->
  `fixup_game_funcs.py` (cwd `N64Recomp`, exactly once) ->
  `cmake --build .` (cwd `build`, needs
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`).
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The driver's own `CRASH: N` summary counts occurrences of the LITERAL
  STRING `[CRASH]`; grep `[CRASH] caught signal` for actual crash event
  counts. The launch-log's own `--- summary ---` block also prints
  `exit=2: N` (crash-exit count) — cross-check both. Note `exit=1: N` in
  that summary is a separate, much-noisier counter (thousands per run,
  unrelated to crash-exit) — do not confuse it with `exit=2`.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions.
- Verify a fresh binary before trusting any result: `strings
  build/RogueSquadron64Recomp | grep '<your-new-tag>'` plus `ls -la
  build/RogueSquadron64Recomp` vs. the soak's start time.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (still ~407 KB+ / ~6000+ lines,
flagged 44+ sessions without action).

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope). Also still not fixed: the script's non-idempotency
bug found s250 (`rs_malloc` entry-capture patch stacks duplicate
declarations on repeat invocation).

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.
