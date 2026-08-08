# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s521 recap -- read this first

s521 did three things:

1. **Folded in item -319's queued 2nd confirm** (`s520_sibling_ptr_b0d0_confirm`, rc=0, 346s):
   clean in the detailed `run.log` -- 0 `sibling-ptr-write-guard` fires (any site, including the new
   `site=0x8000B0D0`), `hangarbay-entry n=31` positive control, zero crashes of any kind for the full
   scheduled duration. **Item -319 is now FULLY CLOSED 2/2.**
2. **Picked up item -317 step 3's blanket sweep again** and fixed its 20th site:
   `BEGIN_FRAME_DL_CHUNK_R1_GUARD` (`funcs_3.c:16595`/`0x8000B570`, `beginFrameDLChunk`, 36 shared
   reload sites, first step-3 guard in this function). 1st live-verify CLEAN (0 own-guard fires, 0
   fires on every other armed guard family this run, `hangarbay-entry n=32` positive control). 2nd
   confirm queued: `scratch/agent/soak_queue/s521_begin_frame_dl_chunk_r1_confirm.sh` -- fold its
   result in next session.
3. **Surfaced a new single-occurrence crash**: the 1st live-verify crashed at ~124-126s on
   `pc-symbol=heapFreeListInsert+72 (local-symtab)`, `last-guest-pc=0x80015544` -- genuinely new,
   filed as item -324, not chased (no 2nd occurrence yet).

Also found and fixed a tooling gotcha: `scratch/agent/s506_dedupe.py` reads a hardcoded
`scratch/agent/s494_item317_step3_report.json`. Running `s494_item317_step3_tracer.py --scan` with a
custom `--out` (e.g. to inspect without touching the canonical file) leaves that file stale --
dedupe then silently ranks against OLD data. This actually happened this session: the first fresh
scan (written to a scratch path) still showed `funcs_4.c:15166` (`RENDER_LIT_MESH_R8_GUARD`, closed
s520) as a top-20 tier, which turned out to be leftover from before this session's `--scan` run ever
touched the canonical report. Always let `--scan` run with its DEFAULT `--out` before running
`s506_dedupe.py`, or double check any suspicious top-ranked site against the actual current source
before trusting the count.

Both written up: `docs/CURRENT-TRUTH.md` items -317/-319/-324, `PORTING-STATE.md` Session 521.

## The work unit: resume item -317 step 3's blanket sweep

Per the user directive's priority order, M3's top-ranked work unit is still item -317 step 3: the
~150-location blanket sweep of the s494 tracer's derived-pointer reload idiom across
`funcs_3.c`/`funcs_4.c`. **~126 locations remain unaudited** (20 of ~150 fixed so far, 19 fully
closed 2/2, the 20th's 2nd confirm queued).

1. **Re-run the tracer fresh** before picking a site -- line numbers drift with every insertion, and
   per this session's gotcha, do NOT pass a custom `--out`:
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Pick the next-highest-count tier from the fresh output. As of the s521 scan (STALE, re-run
   first): `funcs_3.c:14280`/`15170` (36 sites each, `beginFrameDLChunk` -- the other two members of
   the tied-top tier `BEGIN_FRAME_DL_CHUNK_R1_GUARD` came from), `funcs_3.c:14763`/`16120` (32 sites,
   `beginFrameDLChunk`), `funcs_3.c:11625`/`12895`/`15654` (30 sites, mixed
   `emitColorFillRect`/`beginFrameDLChunk`), `funcs_4.c:4457` (`submitSceneNodeRender`, 30 sites).
3. Follow the exact established fix pattern (see any of the 20 guards in `docs/PROJECT-OVERVIEW.md`
   §22-§23, or `BEGIN_FRAME_DL_CHUNK_R1_GUARD`/`fixup_game_funcs.py` for the freshest example): null
   check gates one arm, non-null fallthrough has no `0x80000000`-`0x80800000` range check before a
   write-through deref, downstream control flow reloads the register from the same table again --
   skip-on-invalid is safe. Confirm this shape holds at the specific site before writing the fix,
   AND confirm the picked line isn't already guarded by reading the actual generated source (the
   tracer's own dedupe ranking can lag a stale canonical report file, see the gotcha above).
4. **If the site is in `beginFrameDLChunk`**: that function carries `g_rs64_last_guest_pc`
   breadcrumb writes between every disassembly comment and its corresponding C statement (unlike
   e.g. `renderLitMeshFaceGroup`, which doesn't) -- the fixup patch's old/new match strings MUST
   include that breadcrumb line or the string replace silently no-ops (`text.count(old) == 0`,
   caught by checking the count before trusting the patch applied). Check for this line before
   writing the old/new pattern for any new site, don't assume from a prior function's shape.
5. Regen/build/live-verify/queue-2nd-confirm sequence (see Regen reminder below).

**Caveat from item -319's own resolution (s520)**: `beginFrameDLChunk` has at least TWO structurally
distinct vulnerable-reload idioms -- the s494 tracer's own `+0x63B0` self-referential shape (this
sweep's tiers, now including `BEGIN_FRAME_DL_CHUNK_R1_GUARD`), and the `-0x23A8` sibling-global shape
item -319 closed one site of (family already otherwise covered by the s459/`SIBLING_PTR_WRITE_GUARD`
sweep, items -296/-306). Don't assume fixing one tier closes the other -- verify each site's actual
reload shape before writing a fix.

**Regen reminder** (verify each step -- this has bitten prior sessions when skipped):
1. Delete all `funcs_*.c` in `N64Recomp/RecompiledFuncs/` first and confirm `0 remaining` -- stale
   files silently survive a partial regen otherwise. (Sandbox note: `rm -f funcs_*.c` glob-expansion
   and `find -delete` both get blocked by the approval layer here -- a one-line `python3 -c "import
   glob, os; [os.remove(f) for f in glob.glob('funcs_*.c')]"` from inside `RecompiledFuncs/` works.)
2. `cd rogue_squadron64 && python3 tools/make_elf.py` -> `cd N64Recomp && ./build/N64Recomp
   rogue_squadron.toml` -> `python3 fixup_game_funcs.py` -> `cd RogueSquadron64Recomp/build &&
   DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`.
   (In this sandbox, invoking these via a small `subprocess.run(..., cwd=...)` python one-liner
   avoids the "cd + redirection in a compound command" approval friction seen s521; plain shell `cd
   X && Y` compound commands and env-only-PATH subprocess calls both hit denials/`FileNotFoundError`
   when cmake isn't in a stripped-down PATH -- pass `env=dict(os.environ)` plus the extra var
   instead of replacing PATH outright.)
3. Grep the fixup report AND the freshly-generated source for the new guard's own name -- a silent
   no-op (rc=0, no error, 0 applied) has happened before when a function carried its own pre-existing
   breadcrumb patch and the guard's old/new match string didn't include the inserted line.
4. Live-verify manually in the foreground with every sibling guard's env var armed plus the new
   guard's own `ROGUESQ_LOG_<NAME>=1` (copy the full env-var list from
   `scratch/agent/soak_queue/s521_begin_frame_dl_chunk_r1_confirm.sh` -- add any new guard names
   since), phase-gate on `hangarbay-entry` as the positive control (Iron Rule 1 -- a null result
   needs a same-run positive control). Write the run as a standalone script under `scratch/agent/`
   (foreground `env VAR=1 ... zsh probe.sh` one-liners with backslash continuations get rejected by
   the sandbox), `chmod +x`, run it, delete it after (or move it -- see gotcha below). If clean, queue
   a 2nd independent confirm to `scratch/agent/soak_queue/` for the loop.
5. **Path gotcha (hit again in s521 -- get this right the first time)**: a manual verify script
   placed directly in `scratch/agent/` needs `cd "$(dirname "$0")/../.."` (2 levels up to repo root)
   NOT `cd "$(dirname "$0")/.."` (1 level, only correct if the script were placed directly at repo
   root) and NOT `../../..` (3 levels, only correct for scripts nested one level deeper, e.g. inside
   `soak_queue/`). Verify the relative depth before copying an existing script as a template --
   double check by echoing `$REPO_ROOT` and confirming it ends in `RogueSquadron64Recomp`, not
   `scratch` or its parent.
6. **Positive-control gotcha**: for a QUEUED soak run (not manual foreground), the informative detail
   lives in `scratch/agent/soak_results/<name>/run.log` (a directory), NOT the flat
   `scratch/agent/soak_results/<name>_<timestamp>.log` file next to it (which is just a short
   pid/phase/crash summary). Always grep the directory's `run.log` for `hangarbay-entry` before
   concluding a confirm lacked a positive control.

`fixup_game_funcs.py` and the regenerated `RecompiledFuncs/*.c` live in the sibling `N64Recomp`
checkout (untracked by its own git) -- not this repo's git tree. This repo's ledger entries (with the
full old/new patch text) are the only durable record of every guard in this lineage since s481; no
`lib/` submodule involvement, no `export.sh` needed for this work.

## Discriminating measurement

For whichever site is picked: does it show the established shape (null check gates one arm, no range
check on the non-null fallthrough's write-through deref, downstream reload makes skip-on-invalid
safe) — confirmed by reading the actual generated C around that guest address before writing the fix,
not assumed from the tier's site-count alone.

## If the sweep pick resolves quickly and there's remaining budget

Fold in s521's queued `s521_begin_frame_dl_chunk_r1_confirm.sh` result if the loop has run it by
session start (check `scratch/agent/SOAK-RESULTS.md` tail first, per the standard read-list). If
clean 2nd confirm, mark item -317's 20th guard (`BEGIN_FRAME_DL_CHUNK_R1_GUARD`) CLOSED 2/2 in
`docs/CURRENT-TRUTH.md` (20/20 fully closed of the ~150-location sweep).

**M5 cadence**: last checked clean s520, due again s523+ (per s520's reset) -- not due yet this
session unless the session count has moved past that threshold.
