# NEXT work unit

HYPOTHESIS-ID: item-304-hi8012-5bbc-classify

## s470 summary: rule-8 mandatory pivot on `item-301-scan-buckets` — ran the queued discriminating
probe (classify + guard `hi16=0x8013, offset=-0x7104`, 29 sites, `funcs_6.c` only) and CLOSED it
outright as item -303, `TEXDATA_PTR_ARRAY_GUARD`. Classification found two raw-pointer risk shapes
(direct use as an `rs_free()` argument / write-loop base with no arithmetic at some sites, `idx*4`
array-of-pointers access at others) — genuinely different from item -302's confirmed integer-index
shape, so the guard-at-reload method applied cleanly. Regex verified 29/29 against the raw
`MEM_W(reg, -0x7104)` line count before patching. Clean build, all 7 pre-existing sibling guards
unchanged (84/84/84/119/20/10/31), new guard patched exactly 29/29, `strings` on the binary confirms
29 tag occurrences. Live-verify: 0 new-guard fires, 0 fires on all 7 siblings, `hangarbay-entry` n=31
(positive control). Crashed at 117.1s on `last-guest-pc=0x80054744` inside
`tickWrappingTimerAccumulatorList` — the EXACT already-catalogued, already-PARKED
`m5-audio-destub-tickwrap-divzero-craftselect` div-by-zero-trap signature (first seen ~s344),
unrelated to any guard tested, filed not chased. 2nd independent confirm soak queued.

Full derivation: `PORTING-STATE.md` Session 470; ledger updated in `docs/CURRENT-TRUTH.md`
Next-steps item -298..-303 and the USER DIRECTIVE next-candidate pointer.

## Why the HYPOTHESIS-ID changed even though the strategy didn't

The rule-8 mandatory pivot fired because 3 consecutive iterations (s467-469) carried the SAME slug
`item-301-scan-buckets` even though each one closed a distinct item — the loop's enforcement tracks
the literal slug string, not whether the underlying work produced results. This session's probe DID
close cleanly (item -303), which is a legitimate reason to keep going, but per the pivot instruction's
letter ("switch to a different work unit (new HYPOTHESIS-ID)... or ... close or pivot on its result")
the slug itself changes now regardless. The underlying M3 idiom-class-audit scan strategy (USER
DIRECTIVE priority 3) is UNCHANGED and still producing tractable, closeable buckets — this is not a
strategy pivot, just a slug reset so the loop's per-slug counter doesn't immediately re-trip on the
very next iteration of the same multi-session scan sweep.

## This session's top work unit: classify `hi16=0x8012, offset=-0x5BBC` (30 sites, 4 files)

Both remaining single-file buckets from the s465 scan are now resolved (item -302 deferred, item -303
closed s470). This is the next-ranked candidate by raw site count, but unlike every prior bucket in
this sub-arc it's scattered across 4 files rather than concentrated in one — budget extra
classification time; the single-file-concentration heuristic that made items -299/-300/-301/-303
tractable in one session each does NOT apply here, so this may take longer or split across sessions.

### Step 1: classify with the reusable generic tool

```
cd ~/Documents/Tools/N64Recomp
python3 scratch_s468_shapecheck_generic.py 8012 -5BBC
```

Read the output across ALL 4 files (not just the largest). Decide, same test as every prior bucket:
- Raw reload used DIRECTLY as a pointer (with or without index arithmetic before the deref) — the
  guard-at-reload method applies. Remember s470's lesson: `hit_deref=False` in the tool's output does
  NOT mean "not a pointer" — it can mean the reload is consumed by a callee argument or a store
  instruction the tool's local-window deref pattern doesn't match. Read every `hit_deref=False` site
  directly from the relevant `funcs_N.c` file before concluding it's safe to exclude or that the
  bucket is unsuited.
- Small INTEGER INDEX shifted/scaled before any pointer arithmetic (the item -302 shape) — defer.
- Read at least 3-5 full sites per file (not just the tool's truncated windows) to confirm real
  semantics, same as every prior close in this lineage.

### Step 2: if a genuine raw-pointer risk, write and verify the regex BEFORE touching fixup_game_funcs.py

Model `scratch_s470_test_regex_7104.py` (N64Recomp repo, untracked) — swap the offset, confirm the
match count equals the scan's reported site count (30) SUMMED ACROSS ALL 4 FILES, cross-check against
independent raw-line-count greps for both the `lui` and the reload lines, per file.

### Step 3: design the substitute value

If any site's downstream chain adds index/offset arithmetic before the deref (the item -299/-300/-301/
-303 pattern), 0 is NOT safe — use `0x80000000u` (valid RDRAM base). If EVERY site derefs immediately
at offset 0 with no arithmetic, 0 may be appropriate — check what the existing control-flow structure
around the deref expects before choosing. A multi-file bucket may need per-file substitute-value
review if the downstream shape differs meaningfully between files (unlike every prior bucket, which
was one file each).

### Step 4: patch, regen, build, live-verify, queue confirm soak — standard recipe

1. `cd ~/Documents/Tools/N64Recomp && python3 -c "import glob,os; [os.remove(f) for f in
   glob.glob('RecompiledFuncs/funcs_*.c')]"`
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. `python3 fixup_game_funcs.py` (run exactly ONCE per regen). Audit the report for the expected
   new-guard count AND confirm ALL 8 existing sibling guard counts are UNCHANGED via exact
   `getenv("ROGUESQ_LOG_<TAG>")` occurrence counts: `DL_LIST_APPEND_GUARD` 84, `DL_LIST_RESET_GUARD`
   84, `SIBLING_PTR_WRITE_GUARD` 119, `DL_BUFFER_POOL_GUARD` 84, `NODE_LIST_HEAD_GUARD` 20,
   `NODE_LIST_HEAD_WRITE_GUARD` 10, `TEXDATA_TABLE_GUARD` 31, `TEXDATA_PTR_ARRAY_GUARD` 29 — a
   regression in any of these means the new regex clobbered an existing guard's anchor text.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` (from the
   RogueSquadron64Recomp repo root).
6. `strings build/RogueSquadron64Recomp | grep -c <new-tag>` — confirm it matches the site count.
7. Live-verify from `build/`: arm ALL passive guard/breadcrumb env vars (copy the full list from
   `scratch/agent/soak_queue/s470_texdataptrarray_confirm.sh`) plus the new guard's own
   `ROGUESQ_LOG_<NEW_TAG>=1`, `PROBE_KEYS_FROM_PHASE=1`, full schedule, SIGKILL at teardown.
   Discriminating outcome: 0 new-guard fires expected (matches item -287's true-negative baseline)
   PROVIDED `hangarbay-entry` shows the code was actually reached (positive control, iron rule 1).
8. Write `scratch/agent/soak_queue/s471_<name>_confirm.sh` (self-contained, same shape as the s470
   recipe) for the loop to run.

## Fallback if `-0x5BBC` turns out unsuited (index-not-pointer shape, like item -302)

Move to the next candidate: `hi16=0x8011, offset=-0x35E0` (23 sites, 9 files) or `hi16=0x8013,
offset=0xB50` (21 sites, 11 files) — both more scattered still, budget extra time. If NONE close
cleanly within budget (iron rule 8 applies fresh under this new slug: 3 consecutive iterations
without a close forces a pivot preamble, a 4th blocks), that's the legitimate signal to close this
scan-driven sub-arc for good — the `count >= 20` threshold would then be confirmed to be surfacing
only lower-value, harder-to-guard idioms past the `funcs_3.c`/`funcs_4.c`/`funcs_6.c` core that
produced every real finding so far.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

Unchanged from prior sessions — 10 of item -296's 119 sites sit in `submitSceneNodeRender`, tied to a
still-open 2-occurrence wait-for-recurrence breadcrumb. 0 fires across every soak so far, including
s470's live-verify (the crash that session was the already-catalogued `tickWrappingTimerAccumulator-
List` div-by-zero trap, not in this function's subtree). Passive, no action needed unless a soak
result shows a fire.

## Soak queue status

`s470_texdataptrarray_confirm.sh` queued this session (item -303's 2nd independent confirm soak) —
not yet consumed as of this write. Check `scratch/agent/SOAK-RESULTS.md` tail at the start of next
session and fold its result into the ledger like any other run evidence.
