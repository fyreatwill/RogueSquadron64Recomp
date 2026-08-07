# NEXT work unit

HYPOTHESIS-ID: item-301-scan-buckets

## s469 summary: MAINTENANCE iteration (Step 0 triggered at 61644 bytes). Folded s468's queued 2nd
confirm soak for item -301 (`TEXDATA_TABLE_GUARD`) into the ledger — 0 fires on the new guard and all
6 siblings, `hangarbay-entry` n=31 (positive control), true-negative result holds a 2nd time. Crashed
on a NEW single-occurrence signature (`findOrCreateMaterial+776`/`emitMaterialTexturedDLAlt`,
`last-guest-pc=0x80010b7c`, inside `submitSceneNodeRender`'s call subtree) — filed, not chased (the
sibling-ptr-write-guard instrument covering that function's own open breadcrumb did not fire, so this
is not confirmed as the same mechanism). Migrated items -298 through -302's full detail from
`docs/CURRENT-TRUTH.md` into a new `docs/PROJECT-OVERVIEW.md` §18; net shrink of exactly 200 lines in
CURRENT-TRUTH.md (296 deletions, 96 insertions per `git diff --stat`). No experiment ran this
session — maintenance iterations don't run experiments.

Full derivation for every closed/deferred bucket, and this session's soak fold-in: `docs/PROJECT-
OVERVIEW.md` §18, `PORTING-STATE.md` Session 469.

## This session's top work unit (unchanged from s468 — carried forward, not yet attempted):
classify `hi16=0x8013, offset=-0x7104` (29 sites, `funcs_6.c` only)

Same file as item -301's own close (`TEXDATA_TABLE_GUARD`) — plausibly a sibling texture-management
idiom, and per the established lesson (single-file concentration, not raw site count, is the
tractability signal), this is the most promising remaining candidate even though its raw count (29)
is lower than `hi16=0x8012,offset=-0x5BBC`'s 30 across 4 files.

### Step 1: classify, using the now-reusable generic tools

`scratch_s468_shapecheck_generic.py` (N64Recomp repo, untracked) is already parameterized — run it
directly, no need to write a new script first:

```
cd ~/Documents/Tools/N64Recomp
python3 scratch_s468_shapecheck_generic.py 8013 -7104
```

This dumps the normalized instruction-chain shapes between the reload and the first local
dereference (or a return/branch/20-instruction cap). Read the output and decide:
- If the raw reload register is used DIRECTLY as a pointer (with or without index arithmetic before
  the deref, like items -299/-300/-301) — regardless of how many distinct downstream chain shapes
  exist — the guard-at-reload method applies cleanly. Write a per-offset classify script modeled on
  `scratch_s468_classify_7ce4.py` if you want per-site line dumps too, but it's not strictly required
  once the generic shapecheck output is read.
- If the reload is instead a small integer INDEX immediately shifted/scaled before ANY pointer
  arithmetic touches it (the item -302 shape) — defer, don't force a guard, and move to the next
  bucket in the ranked list below.
- Read at least 3-5 full sites directly from `RecompiledFuncs/funcs_6.c` (not just the tool's
  truncated windows) to confirm real semantics before committing, same as item -301's manual
  `freeTextureDataSlot` read.

### Step 2: if a genuine raw-pointer risk, write and verify the regex BEFORE touching fixup_game_funcs.py

Model `scratch_s468_test_regex_70f8.py` (N64Recomp repo, untracked) — swap the offset, confirm the
match count equals the scan's reported site count, cross-check against independent raw-line-count
greps for both the `lui` and the reload lines.

### Step 3: design the substitute value

If the reload's raw value flows into further arithmetic before any deref (like item -301's `idx*36`
pattern), 0 is NOT safe as a substitute — use `0x80000000u` (valid RDRAM base) instead, per the
`TEXDATA_TABLE_GUARD` precedent. If the reload derefs IMMEDIATELY at offset 0 with no arithmetic
(like `DL_BUFFER_POOL_GUARD`/`GENERIC_CACHE_GUARD`), 0 may be appropriate — check what the existing
branch/control-flow structure around the deref expects before choosing.

### Step 4: patch, regen, build, live-verify, queue confirm soak — standard recipe

1. `cd ~/Documents/Tools/N64Recomp && python3 -c "import glob,os; [os.remove(f) for f in
   glob.glob('RecompiledFuncs/funcs_*.c')]"`
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. `python3 fixup_game_funcs.py` (run exactly ONCE per regen). Audit the report for the expected
   new-guard count AND confirm ALL 7 existing sibling guard counts are UNCHANGED via exact
   `getenv("ROGUESQ_LOG_<TAG>")` occurrence counts: `DL_LIST_APPEND_GUARD` 84, `DL_LIST_RESET_GUARD`
   84, `SIBLING_PTR_WRITE_GUARD` 119, `DL_BUFFER_POOL_GUARD` 84, `NODE_LIST_HEAD_GUARD` 20,
   `NODE_LIST_HEAD_WRITE_GUARD` 10, `TEXDATA_TABLE_GUARD` 31 — a regression in any of these means the
   new regex clobbered an existing guard's anchor text.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` (from the
   RogueSquadron64Recomp repo root).
6. `strings build/RogueSquadron64Recomp | grep -c <new-tag>` — confirm it matches the site count.
7. Live-verify from `build/`: arm ALL passive guard/breadcrumb env vars (copy the full list from
   `scratch/agent/soak_queue/done/s468_texdatatable_confirm_20260807-153023.sh`) plus the new guard's
   own `ROGUESQ_LOG_<NEW_TAG>=1`, `PROBE_KEYS_FROM_PHASE=1`, full schedule, SIGKILL at teardown.
   Discriminating outcome: 0 new-guard fires expected (matches item -287's true-negative baseline)
   PROVIDED `hangarbay-entry` shows the code was actually reached (positive control, iron rule 1).
8. Write `scratch/agent/soak_queue/s470_<name>_confirm.sh` (self-contained, same shape as the s468
   recipe) for the loop to run.

## Fallback if `-0x7104` turns out unsuited (index-not-pointer shape, like item -302)

Move to the next candidate: `hi16=0x8012, offset=-0x5BBC` (30 sites, 4 files) or `hi16=0x8011,
offset=-0x35E0` (23 sites, 9 files) or `hi16=0x8013, offset=0xB50` (21 sites, 11 files) — all more
scattered, budget extra time. If NONE close cleanly within budget (iron rule 8: 3 consecutive
iterations on this slug without a close forces a pivot preamble, a 4th blocks), consider whether the
scan's `count >= 20` threshold is now surfacing genuinely lower-value, harder-to-guard idioms than
the `funcs_3.c`/`funcs_4.c`/`funcs_6.c` core that produced every real finding so far — a legitimate
signal to close this scan-driven sub-arc.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions — 10 of item -296's 119 sites sit in `submitSceneNodeRender`, tied to a
still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far, including
s469's fold-in (the new `findOrCreateMaterial` crash sits in this function's call subtree but did NOT
trip this guard). Passive, no action needed unless a soak result shows a fire.

## Soak queue status

Empty as of this session end — `s468_texdatatable_confirm.sh` was already consumed and moved to
`soak_queue/done/` before this session started. Nothing new queued this session (no code change ran;
this was a maintenance-only iteration). Check `scratch/agent/SOAK-RESULTS.md` tail at the start of
next session regardless, per standard practice.
