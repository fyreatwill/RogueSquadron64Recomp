# NEXT work unit

HYPOTHESIS-ID: item-300-5b48-scan

## s466 CLOSED item -299 (`DL_BUFFER_POOL_GUARD`, global `0x801163FC`, 84/84 sites) outright

Full derivation, fix, build/live-verify results, and confirm-soak recipe: `docs/CURRENT-TRUTH.md`
item -299, `PORTING-STATE.md` Session 466. 0 crash from the guard itself, 0 `dl-buffer-pool-guard`
fires (matches item -287's established true-negative baseline for this whole idiom-class family),
0 fires/no regression on every sibling guard (`DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`/
`SIBLING_PTR_WRITE_GUARD`), `hangarbay-entry` n=32 (positive control, reachable). Crashed later on
the already-catalogued `coalesceFreeHeapBlocks+4424` heap-walker family (s354-366), unrelated —
filed, not chased. Confirmation soak queued: `scratch/agent/soak_queue/s466_dlbufferpool_confirm.sh`
(not yet run by the loop as of this write — check `scratch/agent/SOAK-RESULTS.md` tail next
session and fold its verdict into the ledger like any other soak result before starting new work).

## This session's top work unit: classify the next candidate bucket from s465's scan

s465's from-scratch codebase-wide `lui+lw` frequency scan (`scratch_s465_scan.py`, N64Recomp repo,
untracked — re-run it fresh or re-read its saved output if still on disk) found several buckets
beyond the now-closed `0x63FC`. Highest-priority next candidate, ranked by concentration in the
`funcs_3.c`/`funcs_4.c` lineage core that has produced every real finding in this whole M3
idiom-class arc:

**`hi16=0x8012, offset=-0x5B48`** (global `0x8011A4B8`, 20 sites, `funcs_3.c`/`funcs_4.c` only —
the smallest and most concentrated remaining bucket, worth checking first specifically because a
clean small population is more likely to close outright in one session).

### Step 1: classify all 20 sites' downstream use

Write `scratch_s467_classify_5b48.py` (or similarly numbered — check the actual session number at
start of work) modeled directly on `scratch_s465_classify_63fc.py` and `scratch_s466_shapecheck_
63fc.py` (both N64Recomp repo, untracked): for each of the 20 raw `lui $reg,0x8012; lw
$reg,-0x5B48($reg)` reload sites, capture the downstream use of the reloaded register (deref-read,
direct-write, compare-only, or something else) and bucket by shape. Read at least 5 samples spread
across the population before assuming a single shared shape — every prior "assume it's identical"
shortcut in this lineage (`DL_LIST_APPEND_GUARD`'s own 111-site rescope at s463, `SIBLING_PTR_
WRITE_GUARD`'s 14 outliers) turned out to hide a second population, so don't skip this the way s465
initially only sampled `0x63FC` at 5 points before s466 had to go back and prove it programmatically
across all 84.

### Step 2: if a DIRECT_WRITE+DEREF_READ (or similar CRASH-RISK) shape emerges, do the FULL
normalized-shape audit BEFORE designing the patch

Apply s466's own lesson directly: don't sample 5 sites and assume adjacency/uniformity holds for
all 20 — write the equivalent of `scratch_s466_shapecheck_63fc.py` for this offset up front (one
extra script, cheap) rather than deferring it to a second session the way item -299 needed two
sessions (s465 discover, s466 verify+fix). If the read-then-conditional-write idiom recurs
identically, the s466 fix pattern (guard the read alone, force a nonzero sentinel to skip the write
branch on invalid reload) is DIRECTLY reusable — same env-var/log-tag/static-counter skeleton, new
tag e.g. `DL_BUFFER_POOL2_GUARD` or a name matching whatever the actual field turns out to be.

### Step 3: patch, regen, build, live-verify, queue confirm soak — standard recipe

1. `cd ~/Documents/Tools/N64Recomp && python3 -c "import glob,os; [os.remove(f) for f in
   glob.glob('RecompiledFuncs/funcs_*.c')]"` (Python `os.remove` over `glob`, NOT bare `rm -f`,
   per the standing sandbox-glob caveat — item -20).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. `python3 fixup_game_funcs.py` — audit the report for the expected `x20` (or split count) and
   confirm sibling guard counts (`DL_LIST_APPEND_GUARD` 84, `DL_LIST_RESET_GUARD` 84, `SIBLING_
   PTR_WRITE_GUARD` 119, `DL_BUFFER_POOL_GUARD` 84) are UNCHANGED — a regression there means the
   new regex accidentally clobbered an existing guard's anchor text.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from the
   RogueSquadron64Recomp repo root (or `cd build && cmake --build . -j8`).
6. `strings build/RogueSquadron64Recomp | grep -c <new-tag>` — confirm it matches the site count.
7. Live-verify from `build/`: arm ALL passive guard/breadcrumb env vars (copy the full list from
   `scratch/agent/soak_queue/s466_dlbufferpool_confirm.sh`) plus the new guard's own
   `ROGUESQ_LOG_<NEW_TAG>=1`, `PROBE_KEYS_FROM_PHASE=1`, full schedule, SIGKILL at teardown.
   Discriminating outcome: 0 new-guard fires expected (matches this whole idiom class's established
   true-negative baseline, item -287) PROVIDED `hangarbay-entry` (or equivalent) shows the code was
   actually reached (positive control, iron rule 1).
8. Write `scratch/agent/soak_queue/s467_<name>_confirm.sh` (self-contained, same shape as
   `s466_dlbufferpool_confirm.sh`) for the loop to run.

## Fallback if `-0x5B48` turns out to be COMPARE_ONLY / benign, or not cleanly uniform in
reasonable time

Move to the next bucket in priority order (all from s465's scan, all still unexamined):
`hi16=0x8013,offset=0x7CE4` (45 sites, 9 files — more scattered, lower priority than the
`funcs_3.c`/`funcs_4.c`-only buckets), `hi16=0x8013,offset=-0x70F8` (31, `funcs_6.c` only),
`hi16=0x8012,offset=-0x5BBC` (30, 4 files), `hi16=0x8013,offset=-0x7104` (29, `funcs_6.c` only),
`hi16=0x8011,offset=-0x35E0` (23, 9 files), `hi16=0x8013,offset=0xB50` (21, 11 files).

## Soak queue status

`scratch/agent/soak_queue/s466_dlbufferpool_confirm.sh` is queued as of this session end (not yet
run by the loop) — check `scratch/agent/SOAK-RESULTS.md` tail at the start of next session and fold
its verdict into the ledger before starting new work, per the standing soak-queue consume step.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions — 10 of item -296's 119 sites sit in `submitSceneNodeRender`, tied to
a still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far including
s466's (this session's own live-verify run also showed 0 for this guard). Passive, no action needed
unless a soak result shows a fire.
