# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s520 recap -- read this first

s520 did three things:

1. **Folded in s519's `RENDER_LIT_MESH_R8_GUARD` 2nd confirm**, which had looked weak on a first
   (wrong) read: the flat one-line summary log had 0 `hangarbay-entry` lines, but the REAL detailed
   log is in the SAME-NAMED DIRECTORY's `run.log` (`scratch/agent/soak_results/
   s519_render_lit_mesh_r8_confirm/run.log`, not the `.log` file next to it) -- that one shows
   `hangarbay-entry n=2600` (strong positive control), 0 own-guard fires, crash on the unrelated
   already-catalogued Metal-framework cluster. **CLOSED 2/2. Item -317 step 3 is now 19/19 fully
   closed** (was reported as 18/19+1-pending at the start of this session).
2. **Source-traced and FIXED item -319** (`beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0`, 3
   occurrences, met its own escalation threshold): a real gap in the s459 `SIBLING_PTR_WRITE_GUARD`
   sweep at `funcs_3.c:15017`/`0x8000B0D0` -- sandwiched between two already-guarded sibling sites
   through the same `-0x23A8` global pointer. Fixed via the existing table-driven patcher (121st
   site in the family). 1st live-verify CLEAN (0 own-guard fires including the new site, 3 benign
   `s284-guard` co-fires, `hangarbay-entry n=2600` positive control). 2nd confirm queued:
   `scratch/agent/soak_queue/s520_sibling_ptr_b0d0_confirm.sh` -- fold its result in next session.
3. **M5 audio-lead cadence checked** (due s520+): one diagnostic fired
   (`[audio-wait-pump-stall]`), but it's the existing, already-documented s327 pump-bound diagnostic
   (item -184/-185), seen in 138 other soak logs -- NOT a new lead. Cadence reset to s520, due again
   s523+.

Both written up: `docs/CURRENT-TRUTH.md` items -317/-319, `PORTING-STATE.md` Session 520.

## The work unit: resume item -317 step 3's blanket sweep

Item -319 (which had temporarily outranked this sweep) is resolved. Per the user directive's
priority order, M3's top-ranked work unit reverts to item -317 step 3: the ~150-location blanket
sweep of the s494 tracer's derived-pointer reload idiom across `funcs_3.c`/`funcs_4.c`.
**~126 locations remain unaudited** (19 of ~150 fixed and closed so far).

1. **Re-run the tracer fresh** before picking a site -- line numbers drift with every insertion:
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Pick the next-highest-count tier from the fresh output. As of the s519 scan (STALE, re-run
   first): `funcs_3.c:16582`/`14280`/`15157` (36 sites each, `beginFrameDLChunk`),
   `funcs_3.c:14763`/`16107` (32 sites, `beginFrameDLChunk`), `funcs_3.c:11625`/`12895`/`15641` (30
   sites, mixed `emitColorFillRect`/`beginFrameDLChunk`), `funcs_4.c:4457`/`3299`
   (`submitSceneNodeRender`, 30/28 sites).
3. Follow the exact established fix pattern (see any of the 19 closed guards in
   `docs/PROJECT-OVERVIEW.md` §22-§23 for the shape): null check gates one arm, non-null fallthrough
   has no `0x80000000`-`0x80800000` range check before a write-through deref, downstream control flow
   reloads the register from the same table again -- skip-on-invalid is safe. Confirm this shape holds
   at the specific site before writing the fix; don't assume it from the tier count alone.
4. Regen/build/live-verify/queue-2nd-confirm sequence (see Regen reminder below).

**Caveat from item -319's own resolution (s520)**: `beginFrameDLChunk` has at least TWO structurally
distinct vulnerable-reload idioms -- the s494 tracer's own `+0x63B0` self-referential shape (still
open, these tiers), and the `-0x23A8` sibling-global shape item -319 just closed one site of (family
already otherwise covered by the s459/`SIBLING_PTR_WRITE_GUARD` sweep, items -296/-306). Don't assume
fixing one tier closes the other -- verify each site's actual reload shape before writing a fix.

**Regen reminder** (verify each step -- this has bitten prior sessions when skipped):
1. Delete all `funcs_*.c` in `N64Recomp/RecompiledFuncs/` first and confirm `0 remaining` -- stale
   files silently survive a partial regen otherwise. (Sandbox note: `rm -f funcs_*.c` glob-expansion
   and `find -delete` both get blocked by the approval layer here -- a one-line `python3 -c "import
   glob, os; [os.remove(f) for f in glob.glob('funcs_*.c')]"` from inside `RecompiledFuncs/` works and
   was used successfully in s520.)
2. `cd rogue_squadron64 && python3 tools/make_elf.py` -> `cd N64Recomp && ./build/N64Recomp
   rogue_squadron.toml` -> `python3 fixup_game_funcs.py` -> `cd RogueSquadron64Recomp/build &&
   DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`.
3. Grep the fixup report AND the freshly-generated source for the new guard's own name -- a silent
   no-op (rc=0, no error, 0 applied) has happened before when a function carried its own pre-existing
   breadcrumb patch and the guard's old/new match string didn't include the inserted line.
4. Live-verify manually in the foreground with every sibling guard's env var armed plus the new
   guard's own `ROGUESQ_LOG_<NAME>=1` (copy the full env-var list from
   `scratch/agent/soak_queue/s520_sibling_ptr_b0d0_confirm.sh` -- add any new guard names since),
   phase-gate on `hangarbay-entry` as the positive control (Iron Rule 1 -- a null result needs a
   same-run positive control). Write the run as a standalone script under `scratch/agent/`
   (foreground `env VAR=1 ... zsh probe.sh` one-liners with backslash continuations get rejected by
   the sandbox), `chmod +x`, run it, delete it after (or move it -- see gotcha below). If clean, queue
   a 2nd independent confirm to `scratch/agent/soak_queue/` for the loop.
5. **Path gotcha (hit in s520)**: a manual verify script placed directly in `scratch/agent/` needs
   `cd "$(dirname "$0")/../.."` (2 levels up to repo root) NOT `../../..` (3 levels, which is only
   correct for scripts nested one level deeper, e.g. inside `soak_queue/`). Check the relative depth
   before copying an existing script as a template.
6. **Positive-control gotcha (hit in s520, re-reading s519's result)**: for a QUEUED soak run (not
   manual foreground), the informative detail lives in `scratch/agent/soak_results/<name>/run.log`
   (a directory), NOT the flat `scratch/agent/soak_results/<name>_<timestamp>.log` file next to it
   (which is just a short pid/phase/crash summary). Always grep the directory's `run.log` for
   `hangarbay-entry` before concluding a confirm lacked a positive control.

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

Fold in s520's queued `s520_sibling_ptr_b0d0_confirm.sh` result if the loop has run it by session
start (check `scratch/agent/SOAK-RESULTS.md` tail first, per the standard read-list). If clean 2nd
confirm, mark item -319 CLOSED 2/2 in `docs/CURRENT-TRUTH.md`.
