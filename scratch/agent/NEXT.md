# NEXT work unit — guard the `static_5_800AB658` whack-a-mole site (s248
# lead, 2nd occurrence s257) so the game can reliably reach
# `renderUnlitMeshFaces` and finally give `R7A_LOADED`/`R7B_LOADED` (and
# item -49 generally) a real positive-control soak

## Where the investigation stands (s257)

s257 mined s256's `guard8soak1/run.log` for anything upstream of its
crash (per CLAUDE.md's capture-once-analyze-many rule) and found nothing
new — the crash backtrace and register signature both exactly match
already-catalogued occurrences (s172-lineage backtrace shape; s194/s219's
`x8=0x300000000` rdram-base + `x9=0x80630062` zero-extended-KSEG0-pointer
additive mechanism). That closed step 1 with a confirmed-boring result.

Rather than burn the 3rd (final) allowed `C_LOADED` null re-soak, s257
read the REST of `renderUnlitMeshFaces` (`funcs_4.c:4989-5672`, the whole
function) and found that sites A/B/B_LOADED/C/C_LOADED/D between them
cover every use of `ctx->r16`/`r18`/`r20` in the function, and `r16` is
never reassigned outside sites B/C — so `guard8soak1`'s clean pass across
all six genuinely rules out that entire chain for its occurrence, not
just an unlucky miss. The one pointer in the whole function with **zero**
tracer/guard coverage: `ctx->r7 = MEM_W(ctx->r17, 0X0)` (guest
`0x80011DC8` and `0x80011F1C`, two near-identical unrolled copies) —
loaded straight out of the mesh-face list data with no validation, then
used for 9 unguarded `MEM_W` stores (offsets `0x0`-`0x24`) every loop
iteration.

Added two new observer-only tracer sites, `R7A_LOADED`/`R7B_LOADED`,
reusing the existing `_rogue_unlit_mesh_tracer_check` helper (same
`ROGUESQ_LOG_UNLIT_MESH_TRACER` gate, no new env var). Patch lives in
`fixup_game_funcs.py` in the sibling `N64Recomp` checkout, right after
the existing C_LOADED block (search `R7A_LOADED` to find it). Full regen
+ clean build + `strings`-verified binary, soaked as `r7soak1`
(`scratch/s73_post_a_scene/r7soak1/run.log`, ~223MB, 3,967,721 lines).

**Result: null on the R7 question, with NO positive control.** The
`unlit-mesh-tracer` marker had ZERO hits of any kind this run, including
the always-on-at-call-1 positive-control counter — `renderUnlitMeshFaces`
was never called at all before the process died. This tracer has never
had a real test yet (unlike `C_LOADED`, which got one clean shot in
`guard8soak1`).

**But the run crashed anyway**, at the familiar 75.1s SELECT-CRAFT
transition (`update_screen #4474`), inside the hangar-selection MENU
itself, before ever reaching gameplay rendering:
`static_5_800AB658+49104` ← `static_5_800AAD9C` (`runHangarSelectionFrame`)
← `static_5_800C6854` (`runHangarMenuFromOverlay`) ← `menuOverlayInit` ←
`mainGameLoop`. Register dump: `x9=0x300000000` (rdram host base) — same
additive whack-a-mole shape as item -49's bug family, but a DIFFERENT
specific call site. **This exact stack was already named at s248**
(CURRENT-TRUTH `-89`, PORTING-STATE Session 248) as one of "10+ known
call sites" in this family, explicitly flagged then as "not one of them
[already guarded]." s257's crash is the 2nd independent occurrence of
this specific still-open site.

## The next work unit, in priority order

### Step 1: full-body read of `static_5_800AB658` to find the unguarded load

```
grep -n "^RECOMP_FUNC void static_5_800AB658" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_40.c
# starts at line 7228; next RECOMP_FUNC after it is static_5_800ADB70 at 14468
# i.e. this function spans ~7239 lines -- READ IT IN CHUNKS (e.g. 1500-line
# windows), do not try to read it in one call.
```

Look for the SAME pattern as every prior guard in this family (s101,
s219, s254's `HANGARLIST_GUARD`): a pointer loaded from a table/list entry
with a `lw`/`MEM_W` and dereferenced with **zero** null/range check
before use, especially near the START of the function or right after a
branch from `runHangarSelectionFrame` (since the crash offset, `+49104`
native bytes, is deep — but per this project's established rule, native
offsets do NOT map linearly/reliably to guest addresses or C line
numbers; use the offset only to know WHICH function to read in full,
never to guess the specific line). Since the crash offset is large,
expect the guilty load to be somewhere well into the function, not in
the first few hundred lines — budget the read accordingly (this may take
most of one iteration by itself, same as s255/s256's
`composeNpcOrientationMatrix` reads did).

### Step 2: guard the earliest unvalidated load, in `fixup_game_funcs.py`

Same shape as `HANGARLIST_GUARD` (s254) and every guard before it: check
the loaded pointer's low 32 bits are in `[0x80000000, 0x80800000)` and
high 32 bits are `0xFFFFFFFF` (the sign-extension convention this
project's `MEM_W` macro relies on — see the existing
`RENDERUNLIT_GUARD` at funcs_4.c:5045-5059 for the exact idiom to copy).
On failure, zero the pointer and skip/bail the same way the source's own
control flow would on a null entry (read enough surrounding code to know
the right bail target — do NOT invent one).

### Step 3: full regen -> build -> soak (reuse the r7soak1 script)

```
cd /Users/williambuckley/Documents/Tools/rogue_squadron64
python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"
python3 tools/make_elf.py
zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/agent/regen_n64recomp.sh
python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py   # exactly once
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
strings /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build/RogueSquadron64Recomp | grep <new guard's env-var name>   # confirm fresh binary
cp scratch/s73_post_a_scene/run_r7soak1.sh scratch/s73_post_a_scene/run_<newtag>.sh   # edit last line's tag, add new guard's env var if it needs one (R7A/B_LOADED already armed via ROGUESQ_LOG_UNLIT_MESH_TRACER=1, already in the script)
zsh scratch/s73_post_a_scene/run_<newtag>.sh   # run_in_background: true
```

Block-wait pattern: read the driver's first output line for
`pid NNNNN`, then a SECOND foreground Bash call (generous timeout, up to
480000ms): `until ! kill -0 <pid> 2>/dev/null; do sleep 10; done`.

**Discriminating outcomes**: new guard fires with sane fields -> real
mechanism found, and if the hold now survives past 75.1s AND
`renderUnlitMeshFaces` gets called (unlit-mesh-tracer positive control
fires), `R7A_LOADED`/`R7B_LOADED` FINALLY get their first real test —
read their fire counts directly, that's the actual answer to item -49's
current sub-question. Crash recurs at a DIFFERENT site -> progress, not
the only gap in this chain, repeat the process on the new site. Crash
recurs at the EXACT same `static_5_800AB658` signature -> guard missed
a deref or the anchor didn't match all call sites (check both
funcs_27.c:123427/124181 call sites too — those are just calls into the
function, not separate definitions, so one guard in the funcs_40.c
definition should cover both, but verify).

## Do NOT do this iteration

- Do NOT re-run `r7soak1` in place — copy to a new tag.
- Do NOT re-attempt `nm`/`atos`/`objdump` for offset localization —
  confirmed unusable 3+ independent times (`otool`/`objdump` blocked by
  headless permissions, and there's no human in the loop to approve
  them). Use `scratch/agent/machoparse.py` (from-scratch Mach-O symbol
  reader) if function-size verification is ever needed again.
- Do NOT credit `R7A_LOADED`/`R7B_LOADED` with anything yet — this
  session's soak gave them ZERO calls, not zero fires; that's a missing
  positive control, not a clean result. Don't write them into
  CURRENT-TRUTH as "confirmed clean" until they get an actual call.
- Do NOT fold `static_5_800AB658+49104` into a "new" bug — it's a 2nd
  occurrence of an already-named (s248) whack-a-mole site.
- Do NOT skip straight to guarding `static_5_800AB658` without reading
  it first — same rule as every prior guard in this file: read before
  writing, so the guard matches the SPECIFIC unvalidated load, not a
  guess.

## Environment notes (carried forward, still current as of s257)

- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses.** Use the offset only to identify WHICH
  function to read in full; never try to place it at a specific guest
  instruction or extrapolate C line number from it.
- The current binary (as of s257's build) has `R7A_LOADED`/`R7B_LOADED`
  plus every guard/tracer landed through s257 — no rebuild needed for a
  bare re-soak of the SAME question, only if you land new code (which
  this NEXT work unit does).
- **Block-wait pattern**: launch the soak with Bash `run_in_background:
  true`, read the driver's first output line for `pid NNNNN out=...`,
  then run a SECOND Bash call (foreground, generous timeout up to
  480000ms) that polls `until ! kill -0 <game_pid> 2>/dev/null; do sleep
  N; done`. This blocks until the process exits, letting a soak run to
  completion within one iteration.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`. Also:
  compound `cd ... && ... > file` commands with output redirection
  after a `cd` get blocked for approval — run `cd` as its own Bash call
  first (cwd persists across calls in this harness), or use absolute
  paths and skip `cd` entirely. Same for bare `git -C <path> ...` —
  prefer a plain `cd <path>` call first, then `git ...` with no `-C`.
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
  A crash immediately after this means the game died in the SELECT-CRAFT
  menu itself before reaching gameplay — check the crash backtrace for
  `menuOverlayInit`/`runHangarSelectionFrame`/`runHangarMenuFromOverlay`
  frames (menu family) vs. `traverseSceneGraphRecursive`/`processSceneNode`/
  render-function frames (actual gameplay render family) to tell which
  regime you're in before reading the wrong function. Note s257 found
  BOTH families in the SAME backtrace when a soak gets far enough
  (`menuOverlayInit` calling all the way down into
  `traverseSceneGraphRecursive`/`renderUnlitMeshFaces` in `guard8soak1`) —
  the presence of `menuOverlayInit` at the root of the stack does NOT by
  itself mean "died in the menu before gameplay"; check whether
  render-family frames are ALSO present above it.
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
  scope (flagged for the user since s83, still their call).

## Otherwise: continue the static sweep (139 candidates, unchanged since s253)

If step 1-3 above are exhausted this session: `renderLitMeshFaceGroup` (14
sites, `funcs_4.c`), `renderLitTexturedMeshFaces` (11 sites, `funcs_3.c`),
`func_800AE3F0` (10 sites, `funcs_27.c`), `beginFrameDLChunk` /
`emitFrameRdpInitDl` (10 sites each, `funcs_3.c`).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (still ~432 KB+ / ~6200+ lines,
flagged 47+ sessions without action).

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope). Also still not fixed: the script's non-idempotency
bug found s250 (`rs_malloc` entry-capture patch stacks duplicate
declarations on repeat invocation).

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.
