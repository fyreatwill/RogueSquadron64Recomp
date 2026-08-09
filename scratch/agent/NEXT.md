# NEXT work unit

HYPOTHESIS-ID: alloc-tail-walk-guard

## s562 recap (read this first)

**Opened item -344: non-r3 freelist dual-walk residual (s560 r3-only gap) + simple-walk, 1st live-verify CLEAN.**

After packing residual re-scan (22 NEEDS_GUARD: **21 packing DEFERRED** write-base=DL cursor s0/s2/appendRdp; freelist branch-only; **1** countDisplayListChunks freelist simple-walk) and dual-walk any-reg enum (129 total; 119 G3+G4 of which **118 r3** — s560 hardcoded r3 only):

- Residual freelist dual-walk NONE: `allocateDisplayListBuffer` `0x80007DA8` r4 + `renderLitMeshFaceGroup` `0x80013EEC` r4 (post-findAndUnlink)
- Applied GUARD2+3+4 x2 (reuse `ROGUESQ_LOG_ALLOC_TAIL_GUARD{2,3,4}`) + `FREELIST_SIMPLE_WALK_GUARD` x1 on `countDisplayListChunks` `0x80007CC8`
- Landed in `fixup_game_funcs.py` s562 block + surgical RecompiledFuncs

**1st live-verify:** hangarbay n=2600, 0 fires on new residual sites, crashed on item -345.

**Folded confirms:**
- Item **-343 FULLY CLOSED 2/2** (s561_alloc_tail_guard2_confirm: hangarbay n=2600, 0 fires; crash catalogued div0 `0x80054744`)
- Item **-342** still 1/2 — 3rd consecutive weak item-306 death; retry2 queued

**Filed item -345:** DIRECT gap after item -322 `HEAPLISTDEQ_ATTR_WRITE_GUARD` `0x8000D92C` → crash `0x8000D944`/`0x8000D94C` (same stack slot base, unguarded 0X4/0X8). Same model as -334/-340.

**Queued:**
- `scratch/agent/soak_queue/s562_non_r3_freelist_walk_confirm.sh` (item -344 2nd confirm)
- `scratch/agent/soak_queue/s562_alloc_tail_guard34_confirm_retry2.sh` (item -342 2nd confirm, 3rd attempt)

## This iteration's work unit

**Fold in s562 confirms from SOAK-RESULTS:**

1. If `s562_non_r3_freelist_walk_confirm` CLEAN (hangarbay double-digit+, 0 regression): mark item -344 FULLY CLOSED 2/2.
2. If `s562_alloc_tail_guard34_confirm_retry2` CLEAN: mark item -342 FULLY CLOSED 2/2. If WEAK again (item -306, hangarbay n<10): discard; consider recipe isolation or accept intermittent weak rate and keep retrying.

**Then pick next M3 class (priority order):**

### Option A — item -345 DIRECT gap fix (RECOMMENDED)
Root-caused same-run: extend `HEAPLISTDEQ_ATTR_WRITE_GUARD` (or sibling family) to cover `0x8000D944`/`0x8000D94C` writes through the same stack-derived base (r3 from `sp+0x3C`). Same model as items -334/-340. One build, one soak, high information.

### Option B — multi-occurrence breadcrumb escalation
Items -332 (2 occ, moderate), -330 (2 weak). Only escalate on a 3rd independent occurrence.

### Option C — residual dual-walk re-scan after -344 closes
Expect freelist-shaped residual EMPTY (packing stays DEFERRED; non-freelist list walks out of scope).

### Hypotheses (for Option A)
1. **H1:** guarding r3 at 0x8000D944/0x8000D94C (same range check as 0x8000D92C) prevents the Bus error and may fire on live corruption.
2. **H2:** r3 is a different pointer than r2 and needs separate provenance (unlikely — same stack slot load).
3. **H3:** skip-on-invalid is unsafe here because later code depends on the write — degrade path needs checking.

### Discriminating measurement
Apply guard; soak with `ROGUESQ_LOG_HEAPLISTDEQ_ATTR_WRITE_GUARD=1` (or new tag); hangarbay double-digit+; either 0 crash at 0x8000D944 or guard fire with matching bad_ptr.

### Exact commands
```bash
# After fold-in of confirms:
# Source around 0x8000D924..0x8000D94C in funcs_3.c heapFreeListDequeue
# Add range-check on r3 before MEM_W(0X4/0X8, r3); fixup_game_funcs.py + surgical
# Build + 1st live-verify soak ~300s
```

Do NOT re-open freelist-node rN/0X0, classic r2/0X4, freelist-walk GUARD4 (-341), or GUARD2 (-343) — FULLY CLOSED. Do NOT re-open packing as freelist-class (DEFERRED, write-base=DL cursor).

## Iron-rule reminders
- Confirm free session number at START before naming.
- Weak early deaths on item -306 `setByteAcrossEntryList+176`/`0x800aafa8` with hangarbay n<10: discard+retry (s548-s562 standing gotcha).
- Never trust 0-fires without double-digit+ hangarbay-entry.
- Kill with SIGKILL; run from build/ with ROM.
- Full guard table: docs/PROJECT-OVERVIEW.md §22-§26.
