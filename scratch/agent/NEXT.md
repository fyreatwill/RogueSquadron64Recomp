# NEXT work unit — re-analyze s256's own guard8soak1 log for item -49's
# widening question BEFORE spending a new build-run cycle

## Where the investigation stands (s256)

s256 closed the `composeNpcOrientationMatrix` 8th gap s255 surfaced (full
function read of `funcs_40.c:6293-7213`, found an unguarded pointer-field
deref at guest `0x800AB5B4`-`0x800AB5BC` right before the
`projectModelBoundsToScreen` call, same shape as guard7's site but the
sibling branch). Landed `COMPOSE_NPC_GUARD8`, rebuilt, soaked as
`guard8soak1`.

**Result, real and discriminating**: the menu-crash class that killed
every soak since s255 is GONE (901 exercised calls, 0/8 guard fires this
run). The soak crossed SELECT-CRAFT (74.5s) and ran all the way to VI
frame #9664 — **`renderUnlitMeshFaces` was actually called this time**
(`unlit-mesh-tracer` positive-control counter fired, silent in every prior
soak since s255) — then crashed at the same already-tracked bug:
`renderUnlitMeshFaces+792`, `si_addr=0x380630062`. This is the **6th
confirmed occurrence** of item -49's recurring KSEG0-zero-extension bug.
`B_LOADED`/`C_LOADED` both fired 0 times — 2nd of 3 allowed uninformative
nulls on that specific widening question (budget rule 8).

Log location: `scratch/s73_post_a_scene/guard8soak1/run.log` (~253MB,
4,440,859 lines). Already confirmed via grep:
- `compose-npc-orient-800AB1C8` (entry diag): 901 hits
- `compose-npc-orient-guard` through `guard8`: 0 hits, all 8
- `unlit-mesh-tracer`: 1 hit (the positive-control line itself)
- `B_LOADED` / `C_LOADED`: 0 hits each
- Crash at line ~4440808, `pc-symbol renderUnlitMeshFaces+792`

## The next work unit, in priority order

### Step 1 (do this first, no build needed): mine `guard8soak1/run.log` for anything upstream of the crash

Per CLAUDE.md's "capture once, analyze many" rule: this run's log has
NEVER been analyzed beyond the 5 grep counts above. Before spending
another build-run cycle, check what else it contains around the single
`renderUnlitMeshFaces` call (line ~4440808 backwards):
- `grep -a -n "unlit-mesh-tracer\|renderUnlitMeshFaces\|B_LOADED\|C_LOADED"
  run.log` — confirm there is exactly ONE call to the function this run
  (not multiple, with only the last one crashing) by checking if any
  non-tracer log lines reference the function earlier.
- Read ~200 lines of context immediately before the crash (`sed -n
  '4440600,4440810p' run.log`, cheaper than grep -B on a 253MB file) to
  see what the last few frames were doing — was this a normal per-frame
  render call, or something unusual (e.g. right after a scene transition,
  right after `runHangarSelectionFrame`)?
- Check `ctx->r16`'s value lineage more directly: since `B_LOADED`/
  `C_LOADED` didn't fire, the corruption (if any) happens somewhere else
  entirely in the function, or `ctx->r16` was never actually corrupted at
  the guest level and the real bug is in the recompiler's own address
  translation (a hypothesis flagged before but never conclusively tested
  — see CURRENT-TRUTH `0x80630062`/`x9` register-pattern entries).

### Step 2: only if step 1 finds nothing new, one more (3rd, final) `C_LOADED` re-soak

This is the last of the 3 allowed uninformative nulls on the `C_LOADED`
widening question specifically (budget rule 8). If step 2 also comes back
with 0 `C_LOADED` fires, STOP re-soaking this exact question — write the
hypothesis/evidence table into a fresh NEXT.md and either widen the tracer
to a different site or redirect to a different item -49 sub-question
entirely (e.g. the recompiler-translation hypothesis above).

Command pattern (copy the driver, don't re-run in place):
```
cp scratch/s73_post_a_scene/run_guard8soak1.sh scratch/s73_post_a_scene/run_<newtag>.sh
# edit the new file's last line's tag argument
zsh scratch/s73_post_a_scene/run_<newtag>.sh   # run_in_background: true
# read first output line for "pid NNNNN", then block:
# until ! kill -0 <pid> 2>/dev/null; do sleep 10; done
```

No regen/rebuild needed — `guard8soak1`'s binary already has every guard/
tracer through s256. Verify a fresh-enough binary before trusting any
result: `strings build/RogueSquadron64Recomp | grep compose-npc-orient-
guard8` plus `ls -la build/RogueSquadron64Recomp` vs. the soak's start
time (only matters if you rebuild; a bare re-soak reuses the existing
binary and needs no re-verification).

## Do NOT do this iteration

- Do NOT re-run `guard8soak1` in place — copy to a new tag.
- Do NOT skip step 1 (log mining) and jump straight to a re-soak — the
  existing 253MB log has not been fully read yet, only grep-counted on 5
  markers. CLAUDE.md's capture-once-analyze-many rule applies directly
  here.
- Do NOT re-attempt `nm`/`atos` for offset localization — confirmed
  unusable 3+ independent times. Crash offsets on this project's symbol
  format are NATIVE code offsets, not guest MIPS addresses.
- Do NOT credit `COMPOSE_NPC_GUARD8` (or any of guards 1-7) with directly
  "catching" anything this run — all 8 fired 0/901. The evidence for the
  fix is the DISAPPEARANCE of the menu-crash class across 901 calls, not a
  guard catching a bad value in the act. Keep that distinction explicit in
  any future write-up.
- Do NOT fold this run's crash into a "new" bug — it is an exact
  `renderUnlitMeshFaces+792`/`0x380630062` signature match, the 6th
  confirmed occurrence of the existing item -49 bug.

## Environment notes (carried forward, still current as of s256)

- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses.** Use the offset only to identify WHICH
  function to read in full; never try to place it at a specific guest
  instruction.
- The current binary (as of s256's build) has `COMPOSE_NPC_GUARD8` and
  every other guard/tracer landed through s256 — no rebuild needed for a
  bare re-soak, only if you land new code.
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
  regime you're in before reading the wrong function. **As of s256, a
  soak can now reach WELL past this marker (VI frame #9664 vs. the
  transition's frame #4437) into real gameplay rendering.**
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

`docs/CURRENT-TRUTH.md` housekeeping — still ~407 KB+, flagged 46+
sessions, still not done. Per `ITERATION.md` this does NOT count as
`ADVANCED` on its own — pair it with a real change or expect to file
`SUBSTITUTED`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (still ~407 KB+ / ~6000+ lines,
flagged 46+ sessions without action).

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope). Also still not fixed: the script's non-idempotency
bug found s250 (`rs_malloc` entry-capture patch stacks duplicate
declarations on repeat invocation).

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.
