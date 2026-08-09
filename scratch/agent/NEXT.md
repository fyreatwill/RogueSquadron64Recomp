# NEXT work unit

HYPOTHESIS-ID: heaplistdeq-attr-write-gap

## s563 recap (read this first)

**Item -345: HEAPLISTDEQ_ATTR_WRITE residual gap after -322 — FIXED, 1st live-verify CLEAN.**

s562 same-run: guard `0x8000D92C` fired `bad_ptr=0x8` → crash `0x8000D944` (r3 reloaded from same
`sp+0x3C`). Extended family to 7 residual sites (bit-0x10 path + L_8000D968 alt):
`0x8000D944`, `0x8000D94C`, `0x8000D964` x2, `0x8000D978`, `0x8000D980`, `0x8000D994`.
Reuse `ROGUESQ_LOG_HEAPLISTDEQ_ATTR_WRITE_GUARD`.

**1st live-verify:** hangarbay n=2600, 0 fires (true-negative), no crash at 0x8000D944.
Crashed on item -320 2nd occurrence (`loadCutsceneAssetsByIndex+1860`/`0x800aafb8`).

**Folded confirms:**
- Item **-342 FULLY CLOSED 2/2** (s562_alloc_tail_guard34_confirm_retry2: hangarbay n=2900, full 300s)
- Item **-344 FULLY CLOSED 2/2** (s562_non_r3_freelist_walk_confirm: hangarbay n=2900)

**Queued:** `scratch/agent/soak_queue/s563_heaplistdeq_attr_gap_confirm.sh`

## This iteration's work unit

**Fold in s563 confirm from SOAK-RESULTS:**
1. If `s563_heaplistdeq_attr_gap_confirm` CLEAN (hangarbay double-digit+, 0 crash at 0x8000D944):
   mark item -345 FULLY CLOSED 2/2.

**Then pick next M3 class (priority order):**

### Option A — residual freelist-class re-scan (after -345 closes)
Expect freelist WRITE residual EMPTY (packing stays DEFERRED). If empty, close freelist write
campaign formally and pivot to a new idiom class (e.g. multi-occurrence breadcrumbs -332 moderate
3rd-occ watch, or a fresh frequency scan of remaining crash PCs).

### Option B — item -320 3rd-occurrence watch only
Do NOT source-trace -320 yet (only 2 occ). Passive passive soaks; escalate only on a 3rd independent
hit with strong hangarbay control.

### Option C — multi-occurrence breadcrumb escalation (-332 at 2 occ moderate)
Only if a 3rd independent occurrence appears in fold-in soaks.

### Hypotheses (for Option A residual re-scan)
1. **H1:** freelist WRITE NEEDS_GUARD residual is EMPTY after -345 (campaign complete).
2. **H2:** more DIRECT gaps exist adjacent to already-guarded stack-slot bases (same -334 model).
3. **H3:** packing sites (DEFERRED) start crashing and need re-classification.

### Discriminating measurement
Tracer re-scan of freelist write shapes after -345 lands; enumerate NEEDS_GUARD residual count.
If 0 freelist-shaped: campaign closed. If >0: rank and fix highest-count lead.

### Exact commands
```bash
# After fold-in of -345 confirm:
# Re-run residual freelist write scan (or source-adjacent gap audit around
# HEAPLISTDEQ_ATTR_WRITE / SIBLING_PTR_WRITE recently closed sites)
# Do NOT re-open packing as freelist-class (DEFERRED, write-base=DL cursor)
```

Do NOT re-open freelist-node rN/0X0, classic r2/0X4, freelist-walk GUARD4 (-341), GUARD2 (-343),
GUARD3+4 (-342), non-r3 dual-walk (-344) — all FULLY CLOSED.

## Iron-rule reminders
- Confirm free session number at START before naming (next is s564).
- Weak early deaths on item -306 `setByteAcrossEntryList+176`/`0x800aafa8` with hangarbay n<10: discard+retry.
- Never trust 0-fires without double-digit+ hangarbay-entry.
- Kill with SIGKILL; run from build/ with ROM.
- Full guard table: docs/PROJECT-OVERVIEW.md §22-§26.
