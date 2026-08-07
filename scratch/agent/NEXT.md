# NEXT work unit

HYPOTHESIS-ID: item-301-scan-buckets

## s468 summary: folded s467's 2nd confirm soak (clean, matches item -300's own result); classified
and DEFERRED item -302 (`hi16=0x8013,offset=0x7CE4`, 45 sites/9 files — a small-integer-index idiom,
not a pointer, structurally unsuited to this guard method); pivoted to and CLOSED item -301
(`TEXDATA_TABLE_GUARD`, `hi16=0x8013,offset=-0x70F8`, 31/31 sites, `funcs_6.c` only)

Full derivation, fix, build/live-verify results, and confirm-soak recipe: `docs/CURRENT-TRUTH.md`
items -301/-302, `PORTING-STATE.md` Session 468.

**The key transferable lesson from this session**: raw site COUNT is not the tractability signal for
this idiom-class-audit method — SINGLE-FILE CONCENTRATION is. The #1-ranked bucket by count (45
sites, 9 files) turned out to be a fundamentally different, harder idiom (small integer index, not a
pointer, 17 distinct downstream shapes, most sites piping the value to a callee rather than
dereferencing locally) and had to be deferred rather than force a speculative guard. The #2-ranked
bucket (31 sites, but ALL in `funcs_6.c`) was a clean, one-session close — same "raw reload used as a
pointer" risk shape as every prior success in this lineage (`DL_LIST_APPEND_GUARD`, `DL_LIST_RESET_
GUARD`, `DL_BUFFER_POOL_GUARD`, `NODE_LIST_HEAD_GUARD`), even though the pointer had array-index
arithmetic (idx*36 in this case) interposed before the actual dereference — that arithmetic doesn't
matter to the guard design AT ALL, because the guard anchors on the reload itself, not on any
downstream deref point. Reuse this signal when picking the next bucket: prefer `funcs_N.c`-only
buckets over multi-file-spread ones of similar or even somewhat higher site count.

## This session's top work unit: classify `hi16=0x8013, offset=-0x7104` (29 sites, `funcs_6.c` only)

Same file as this session's own close (`TEXDATA_TABLE_GUARD`) — plausibly a sibling texture-
management idiom, and per the lesson above, single-file concentration makes this the most promising
remaining candidate even though its raw count (29) is lower than `hi16=0x8012,offset=-0x5BBC`'s 30
across 4 files.

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
  truncated windows) to confirm real semantics before committing, same as this session's manual
  `freeTextureDataSlot` read.

### Step 2: if a genuine raw-pointer risk, write and verify the regex BEFORE touching fixup_game_funcs.py

Model `scratch_s468_test_regex_70f8.py` (N64Recomp repo, untracked) — swap the offset, confirm the
match count equals the scan's reported site count, cross-check against independent raw-line-count
greps for both the `lui` and the reload lines.

### Step 3: design the substitute value

If the reload's raw value flows into further arithmetic before any deref (like this session's `idx*
36` pattern), 0 is NOT safe as a substitute — use `0x80000000u` (valid RDRAM base) instead, per this
session's `TEXDATA_TABLE_GUARD` precedent. If the reload derefs IMMEDIATELY at offset 0 with no
arithmetic (like `DL_BUFFER_POOL_GUARD`/`GENERIC_CACHE_GUARD`), 0 may be appropriate — check what the
existing branch/control-flow structure around the deref expects before choosing.

### Step 4: patch, regen, build, live-verify, queue confirm soak — standard recipe

1. `cd ~/Documents/Tools/N64Recomp && python3 -c "import glob,os; [os.remove(f) for f in
   glob.glob('RecompiledFuncs/funcs_*.c')]"`
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. `python3 fixup_game_funcs.py` (run exactly ONCE per regen — running it twice on the same
   already-patched files is a no-op but wastes time and risks masking a real anchor-drift bug; if
   you need to re-check counts, grep the already-patched `RecompiledFuncs/*.c` files directly
   instead of re-running the script). Audit the report for the expected new-guard count AND confirm
   ALL 7 existing sibling guard counts are UNCHANGED via exact `getenv("ROGUESQ_LOG_<TAG>")`
   occurrence counts (substring `grep -c` on the tag name alone double-counts, since each site's
   block contains the tag string twice — once in the comment, once in the env var name):
   `DL_LIST_APPEND_GUARD` 84, `DL_LIST_RESET_GUARD` 84, `SIBLING_PTR_WRITE_GUARD` 119,
   `DL_BUFFER_POOL_GUARD` 84, `NODE_LIST_HEAD_GUARD` 20, `NODE_LIST_HEAD_WRITE_GUARD` 10,
   `TEXDATA_TABLE_GUARD` 31 — a regression in any of these means the new regex clobbered an
   existing guard's anchor text.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` (from the
   RogueSquadron64Recomp repo root).
6. `strings build/RogueSquadron64Recomp | grep -c <new-tag>` — confirm it matches the site count.
7. Live-verify from `build/`: arm ALL passive guard/breadcrumb env vars (copy the full list from
   `scratch/agent/soak_queue/s468_texdatatable_confirm.sh`) plus the new guard's own
   `ROGUESQ_LOG_<NEW_TAG>=1`, `PROBE_KEYS_FROM_PHASE=1`, full schedule, SIGKILL at teardown.
   Discriminating outcome: 0 new-guard fires expected (matches item -287's true-negative baseline)
   PROVIDED `hangarbay-entry` shows the code was actually reached (positive control, iron rule 1).
8. Write `scratch/agent/soak_queue/s469_<name>_confirm.sh` (self-contained, same shape as
   `s468_texdatatable_confirm.sh`) for the loop to run.

## Fallback if `-0x7104` turns out unsuited (index-not-pointer shape, like item -302)

Move to the next candidate: `hi16=0x8012, offset=-0x5BBC` (30 sites, 4 files) or `hi16=0x8011,
offset=-0x35E0` (23 sites, 9 files) or `hi16=0x8013, offset=0xB50` (21 sites, 11 files) — all more
scattered, budget extra time. If NONE close cleanly within budget (iron rule 8: 3 consecutive
iterations on this slug without a close forces a pivot preamble, a 4th blocks), consider whether the
scan's `count >= 20` threshold is now surfacing genuinely lower-value, harder-to-guard idioms than
the `funcs_3.c`/`funcs_4.c`/`funcs_6.c` core that produced every real finding so far — a legitimate
signal to close this scan-driven sub-arc.

## Soak queue status

`scratch/agent/soak_queue/s468_texdatatable_confirm.sh` is queued as of this session end (not yet run
by the loop) — check `scratch/agent/SOAK-RESULTS.md` tail at the start of next session and fold its
verdict into the ledger before starting new work.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions — 10 of item -296's 119 sites sit in `submitSceneNodeRender`, tied to
a still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far. Passive,
no action needed unless a soak result shows a fire.

## Maintenance note

`docs/CURRENT-TRUTH.md` is now ~61.6 KB (over the 60000-byte Step 0 threshold) after this session's
additions. Next session's Step 0 will trigger a MAINTENANCE iteration — that's expected and fine, not
a problem to pre-empt now.
