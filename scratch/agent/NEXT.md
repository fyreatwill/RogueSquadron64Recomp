# NEXT work unit

HYPOTHESIS-ID: next-idiom-class-candidate

## s464 CLOSED item -298 outright (84/84 `DL_LIST_RESET_GUARD` sites — 70 blanket-regex s463 + 14
per-site-literal-anchor s464). The whole re-scoped `-0x5824` non-canonical population (111 sites) is
now fully accounted for: 27 canonical (folded into `DL_LIST_APPEND_GUARD`), 70 blanket-regex, 14
per-site. See `docs/CURRENT-TRUTH.md` item -298 and `PORTING-STATE.md` Session 464 for full
derivation. Confirmation soak queued: `scratch/agent/soak_queue/s464_dllistreset14_confirm.sh`
(not yet run by the loop as of this writing — check `scratch/agent/SOAK-RESULTS.md` tail first
thing next session and fold its verdict into the ledger).

**No open M3 idiom-class-audit thread remains.** This is the first time since s454 that this
lineage has no active work item — 4 idiom classes closed back-to-back
(`DL_LIST_APPEND_GUARD`/item -291, `SIBLING_PTR_WRITE_GUARD`/item -296, `SONGTEMPO_TABLE_GUARD`/
item -292, `DL_LIST_RESET_GUARD`/item -298) via the same discovery method (a global-deref audit
scoped by the offending offset literal, e.g. `-0x5824`, `-0x23A8`, `0x29C0`).

## This iteration's work unit: pick ONE, in this order

### Option A (preferred first try): a fresh codebase-wide frequency scan for the next comparable
idiom class

The s389-397 arc (`docs/PROJECT-OVERVIEW.md` §14) tried this and got a negative result at the time
— but that was BEFORE 4 more idiom classes were found and closed via the s454-464 arc, so the
scan's own methodology may simply not have been tuned to catch this session's classes. Re-run or
adapt that method: grep every `RecompiledFuncs/funcs_*.c` for `lw \$\w+, -?0x[0-9A-Fa-f]+\(\$\w+\)`
immediately following a `lui $reg, 0x80XX` pair (the reload-a-global idiom every guard in this
whole lineage shares), bucket by the (offset, base-register-source-global) pair, and look for
buckets with a HIGH site count (20+) that don't already have a `ROGUESQ_LOG_*_GUARD` env var wired
up in `fixup_game_funcs.py` (grep `_GUARD` definitions there for the exhaustive already-covered
list: `GENERIC_CACHE_GUARD`, `CACHE_HEAD_A1_GUARD`, `FREELIST_NEXT_GUARD`, `DL_LIST_APPEND_GUARD`,
`DL_LIST_RESET_GUARD`, `SIBLING_PTR_WRITE_GUARD`, `SONGTEMPO_TABLE_GUARD`, `HANGARLIST_GUARD*`,
`GETDATITEM_GUARD`, `S284_GUARD`, `S285_GUARD`, `S390_H2_GUARD`, `COMPOSE_NPC_GUARD*`,
`ANIM_TEX_STREAM_GUARD*`, `HANGAR_BAY_DEREF_GUARD`, `HANGAR_BAY_SCENE_GUARD`,
`MATEXPIRY_GUARD`). A new bucket with 20+ uncovered sites is a strong candidate — read a handful of
sample sites to confirm the shape (does the reload feed a deref like `DL_LIST_APPEND_GUARD`? A
direct write-address like `DL_LIST_RESET_GUARD`/`SIBLING_PTR_WRITE_GUARD`? Something else entirely
needing a new remediation?) before committing to a fix.

### Option B (fallback if A finds nothing above ~20 sites): `BREADCRUMB7`

The last untouched item from the `static5-rename-orphan-sweep` (s445-451 arc,
`docs/PROJECT-OVERVIEW.md` §16) — diagnostic-only, lowest priority of that whole arc's leftovers.
Grep `fixup_game_funcs.py` for `BREADCRUMB7` to find its current (likely unfinished/parked) state
and read what's left.

### Option C (if both A and B are exhausted): step back to M5 audio or reconsider the strategic
priority list

Per `docs/CURRENT-TRUTH.md`'s USER DIRECTIVE section, M5 audio de-stubbing is CLOSED with "no thread
open... needs a genuinely new lead" — don't restart it without one. If A and B both come up empty,
write a BLOCKED with the specific question: no queued M3 idiom-class-audit candidate and no fresh
M5 lead — ask the human whether to resume reactive single-crash chases (explicitly discouraged by
the strategic priority) or open a different investigation thread entirely.

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

10 of item -296's 119 `SIBLING_PTR_WRITE_GUARD` sites are in `submitSceneNodeRender`, the same
function named in a still-open "wait-for-recurrence breadcrumb" (2 independent single-occurrence
crashes, different `last-guest-pc` each time, not confirmed as one bug). 0 fires across every soak
so far, including s463's and s464's. If any future soak shows a `sibling-ptr-write-guard` fire
specifically at one of those 10 sites, that's new evidence worth immediate follow-up — the one
exception to "don't chase breadcrumbs."

## Incidental observation, not chased (s464)

s464's live-verify crashed at ~126s on `pc-symbol=coalesceFreeHeapBlocks+4424`,
`last-guest-pc=0x8000247c`, backtrace `coalesceFreeHeapBlocks <- runVideoFrameTick <-
menuOverlayInit <- mainGameLoop <- mainBootstrapWorker`. This exact signature is the SAME
already-catalogued, already-closed heap-walker background-noise family documented since Session
366 (`m5-audio-destub-coalesce-heap-guard-verify`, closed s366) and reconfirmed multiple times
since (Sessions ~445-451 range). Not a new class, not chased. If it ever starts recurring at a
materially different offset/backtrace, that would be worth a fresh look — this exact
offset+backtrace pairing is not.
