# NEXT work unit

HYPOTHESIS-ID: item-305-hi8011-63d4-classify

## s471 summary: folded item -303's 2nd confirm soak (0 fires, matches the manual pass exactly; a
DIFFERENT crash this time -- a host-side Metal.framework SIGSEGV in `fscache_insert_and_retain`,
same family as the already-catalogued items -10/-9, filed not chased). Then classified and CLOSED
item -304 outright: `MATERIAL_ARRAY_PTR_GUARD`, `hi16=0x8012, offset=-0x5BBC`, 30 `lw` reload sites
across 4 files (`funcs_3.c`x5/`funcs_4.c`x10/`funcs_6.c`x14/`funcs_7.c`x1) -- the FIRST genuinely
multi-file bucket closed in one session in this sub-arc. Single writer `buildAndRegisterDefaultMaterial`
(stores an `rs_malloc()` result); all 30 reader sites showed the same two raw-pointer-reload risk
shapes as item -303 (idx*4 array-of-pointers access, and direct use with no arithmetic including one
`rs_free()` call-argument site). Regex verified 30/30 across all 4 files before patching. Clean
build, all 8 pre-existing sibling guards unchanged, `strings` confirms 30 tag occurrences. Live-verify:
0 new-guard fires, 0 fires on all 8 siblings, `hangarbay-entry` n=34 (positive control) -- and unlike
almost every other session in this sub-arc, this run hit ZERO crashes at all across the full 300s/
250s-keys schedule. 2nd independent confirm soak queued.

Full derivation: `PORTING-STATE.md` Session 471; ledger updated in `docs/CURRENT-TRUTH.md` Next-steps
item -298..-304 and the USER DIRECTIVE next-candidate pointer.

## This session's top work unit: classify `hi16=0x8011, offset=0x63d4` (170 sites, 4 files)

The largest unclaimed bucket in the s465 codebase-wide scan. Confirmed genuinely uncovered by any
existing guard: `grep -n "0x63d4\|0X63D4\|801163D4" ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
returns 0 hits. Global address: `0x80110000 + 0x63d4 = 0x801163D4` -- 0x28 bytes from item -299's
`DL_BUFFER_POOL_GUARD` global (`0x801163FC`), plausibly a sibling struct field, same caution as item
-303 vs -301 (12 bytes apart) -- do NOT assume shared shape without checking directly, siblings in
this codebase have repeatedly turned out to need different guard mechanics.

This is the LARGEST bucket attempted in this sub-arc so far (170 sites vs the previous max of 119 for
item -296, and previous max NEW-guard bucket of 84). Budget significantly more session time than
recent single/multi-file closes; it may not close in one session -- that is an acceptable outcome
(defer or split across sessions) as long as the classification work itself makes real progress and is
written down before the iteration ends.

### Step 1: classify with the reusable generic tool

```
cd ~/Documents/Tools/N64Recomp
python3 scratch_s468_shapecheck_generic.py 8011 63d4
```

Read the output across ALL 4 files (`funcs_6.c`x75, `funcs_3.c`x44, `funcs_4.c`x30, `funcs_7.c`x21),
not just the largest. Same test as every prior bucket:
- Raw reload used DIRECTLY as a pointer (with or without index arithmetic before the deref) — the
  guard-at-reload method applies. Remember the s470/s471 lesson: `hit_deref=False` in the tool's
  output does NOT mean "not a pointer" — it has repeatedly turned out to be a false negative (reload
  consumed by a callee argument, a store instruction, or a deref a few lines past the tool's local
  window). Read every `hit_deref=False` site directly from the relevant `funcs_N.c` file before
  concluding it's safe to exclude.
- Small INTEGER INDEX shifted/scaled before any pointer arithmetic (the item -302 shape) — defer.
- Given the size of this bucket (170 sites), sample generously: read at least 5-8 full sites per
  file, weighted toward files with the most sites (`funcs_6.c` first), before concluding a uniform
  shape holds across all 4 files. A bucket this large is more likely than prior ones to contain a
  genuine shape split (like item -300's read/write split) — actively look for one, don't assume
  uniformity just because the first few sites match.

### Step 2: if a genuine raw-pointer risk, write and verify the regex BEFORE touching fixup_game_funcs.py

Model `scratch_s471_test_regex_5bbc.py` (N64Recomp repo, untracked) — swap the offset to `0x63D4` and
hi16 to `0x8011`, confirm the match count equals 170 SUMMED ACROSS ALL 4 FILES, cross-checked against
independent raw-line-count greps for both the `lui` and the reload lines, per file. Also grep for any
`sw` (write) sites at this same offset — the item -304 bucket had exactly one legitimate writer site
that had to be excluded from the guard scope by construction (regex only matches `lw` chains); check
whether this bucket has one or more writers before assuming a single-writer shape.

### Step 3: design the substitute value

If any site's downstream chain adds index/offset arithmetic before the deref (the item -299/-300/-301/
-303/-304 pattern), 0 is NOT safe — use `0x80000000u` (valid RDRAM base). Given the bucket spans 4
files, check whether the downstream shape (and therefore the substitute-value reasoning) is consistent
across all 4, or whether — like the caution logged for `-0x23a8` below — different files show
different risk profiles requiring per-file substitute-value review.

### Step 4: patch, regen, build, live-verify, queue confirm soak — standard recipe

1. `cd ~/Documents/Tools/N64Recomp && python3 -c "import glob,os; [os.remove(f) for f in
   glob.glob('RecompiledFuncs/funcs_*.c')]"`
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. `python3 fixup_game_funcs.py` (run exactly ONCE per regen — s471 accidentally ran it twice while
   checking one guard's report and confirmed the 2nd pass is harmless/idempotent when the code is
   already patched, but don't rely on that; run it once). Audit the report for the expected new-guard
   count AND confirm ALL 9 existing sibling guard counts are UNCHANGED via exact
   `getenv("ROGUESQ_LOG_<TAG>")` occurrence counts: `DL_LIST_APPEND_GUARD` 84, `DL_LIST_RESET_GUARD`
   84, `SIBLING_PTR_WRITE_GUARD` 119, `DL_BUFFER_POOL_GUARD` 84, `NODE_LIST_HEAD_GUARD` 20,
   `NODE_LIST_HEAD_WRITE_GUARD` 10, `TEXDATA_TABLE_GUARD` 31, `TEXDATA_PTR_ARRAY_GUARD` 29,
   `MATERIAL_ARRAY_PTR_GUARD` 30 — a regression in any of these means the new regex clobbered an
   existing guard's anchor text.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` (from the
   RogueSquadron64Recomp repo root).
6. `strings build/RogueSquadron64Recomp | grep -c <new-tag>` — confirm it matches the site count.
7. Live-verify from `build/`: arm ALL passive guard/breadcrumb env vars (copy the full list from
   `scratch/agent/soak_queue/s471_materialarrayptr_confirm.sh`) plus the new guard's own
   `ROGUESQ_LOG_<NEW_TAG>=1`, `PROBE_KEYS_FROM_PHASE=1`, full schedule, SIGKILL at teardown.
   Discriminating outcome: 0 new-guard fires expected (matches item -287's true-negative baseline)
   PROVIDED `hangarbay-entry` shows the code was actually reached (positive control, iron rule 1).
   Background the run (it takes ~300-350s wall clock); don't foreground-poll it more than a few
   times a minute.
8. Write `scratch/agent/soak_queue/s472_<name>_confirm.sh` (self-contained, same shape as the s471
   recipe) for the loop to run.

## Fallback if `hi16=0x8011, offset=0x63d4` turns out unsuited or doesn't close in-session

Do NOT jump to `hi16=0x8012, offset=-0x23a8` (141 sites) without reading the caution below first --
it is NOT a clean fresh bucket like every other candidate in this scan.

**Caution: `hi16=0x8012, offset=-0x23a8` (141 sites) is PARTIALLY covered, not fresh.** Item -296's
`SIBLING_PTR_WRITE_GUARD` (119 sites, `fixup_game_funcs.py` s459 comment) already guards the
DOWNSTREAM WRITE through this same reload (`MEM_W(OFF, ctx->rN) = VAL` a few lines after the reload),
NOT the reload itself. The 141-vs-119 gap (22 sites) and whether the raw reload needs its OWN guard
(independent of whether its eventual write is already guarded) is unclassified. Before touching this
bucket: (1) confirm whether guarding the reload would be redundant with the existing write guard (if
every one of the 141 reload sites eventually reaches an already-guarded write, a reload-level guard
may add no new safety), or (2) whether some of the 141 sites use the reload in a DIFFERENT way that
the write guard doesn't cover (e.g. a read instead of a write, or a use before the guarded write). This
needs its own dedicated classification pass, not the standard recipe used for every other bucket.

If both `0x63d4` and `-0x23a8` prove intractable this session, the next-ranked genuinely-fresh
candidates are `hi16=0x8011, offset=-0x35e0` (23 sites, 9 files) or `hi16=0x8013, offset=0xb50` (21
sites, 11 files) — both far more scattered than anything closed so far; budget accordingly.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions — 10 of item -296's 119 sites sit in `submitSceneNodeRender`, tied to a
still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far. Passive, no
action needed unless a soak result shows a fire.

## Soak queue status

`s471_materialarrayptr_confirm.sh` queued this session (item -304's 2nd independent confirm soak) —
not yet consumed as of this write. Check `scratch/agent/SOAK-RESULTS.md` tail at the start of next
session and fold its result into the ledger like any other run evidence.
