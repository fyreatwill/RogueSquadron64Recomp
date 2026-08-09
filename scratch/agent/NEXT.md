# NEXT work unit

HYPOTHESIS-ID: alloc-tail-walk-guard

## s560 recap (read this first)

**Opened item -342: residual freelist-walk GUARD3+GUARD4 (alloc-tail family), 1st live-verify CLEAN.**

After s559 closed GUARD3-without-GUARD4 (16 sites), residual scan of walk-to-tail loops found:
- 118 total `L: v1=*v1; v0=*v1; bne L` sites in funcs_3/4
- 20 already GUARD3; **98 residual** with neither
- 88/98 after `findAndUnlinkSmallestEntry` (true freelist walk-to-tail idiom)
- Applied GUARD3 x94 + GUARD4 x92 (`ROGUESQ_LOG_ALLOC_TAIL_GUARD3` / `_GUARD4`)
- Excluded already-covered: DLENTRY_TAIL (3), drainMesh loop peeks (5), scene-node s123 (1)

**1st live-verify:** hangarbay n=2600, 0 fires, crash on catalogued `initVec4TripletFromArgs+68`/
`0x80065e94` (NAN_CHECK family). True-negative baseline.

**2nd confirm queued:** `scratch/agent/soak_queue/s560_alloc_tail_guard34_confirm.sh`

**Also queued:** `scratch/agent/soak_queue/s560_freelist_walk_guard4_confirm_retry.sh` (item -341;
s559 confirm was weak-discarded on item -306).

## This iteration's work unit

**Fold in s560 confirms from SOAK-RESULTS:**

1. If `s560_alloc_tail_guard34_confirm` CLEAN (hangarbay double-digit+, 0 regression): mark item
   -342 FULLY CLOSED 2/2.
2. If `s560_freelist_walk_guard4_confirm_retry` CLEAN: mark item -341 FULLY CLOSED 2/2 (and
   -339/-337 with it). If WEAK again (item -306, hangarbay n<10): discard+re-queue once more.

**Then pick next M3 class:**

### Option A — residual GUARD2 (initial-deref of findAndUnlink return)
emit-dl has GUARD2 on the first `lw $v0, 0x0($aN)` of the walk setup; residual 88 findAndUnlink
sites only null-check the return. Same shape, family-wide.

### Option B — multi-occurrence breadcrumb escalation
Items -332 (2 occ, moderate), -330 (2 weak). Only escalate on a 3rd independent occurrence.

### Option C — packing DL-cursor audit (item -317 DEFERRED residual)
Separate class: write base is DL cursor; freelist reload branch-only.

### Hypotheses (for Option A if taken)
1. **H1:** residual initial-deref crashes exist and GUARD2 catches them.
2. **H2:** null check + GUARD3+GUARD4 is sufficient; GUARD2 is dead/true-negative only.
3. **H3:** some residual initial-derefs already covered (e.g. drainMesh head guards).

### Discriminating measurement
Grep residual sites for bare `lw $v0, 0x0($aN)` without GUARD2/head-guard; apply GUARD2; soak.

### Exact commands
```bash
git log --oneline -3
tail -8 scratch/agent/SOAK-RESULTS.md
# Fold confirms first; if -342 CLOSED 2/2, Option A residual GUARD2 or Option B/C
```

Do NOT re-open freelist-node rN/0X0 or classic r2/0X4 — both residual-empty and FULLY CLOSED.
Do NOT re-open item -342 sites once 2/2 closed (unless GUARD2 is a deliberate new layer).

## Iron-rule reminders
- Confirm free session number at START before naming.
- Weak early deaths on item -306 `setByteAcrossEntryList+176`/`0x800aafa8` with hangarbay n<10:
  discard+retry (s548-s560 standing gotcha).
- Never trust 0-fires without double-digit+ hangarbay-entry.
- Kill with SIGKILL; run from build/ with ROM.
- Full guard table: docs/PROJECT-OVERVIEW.md §22-§26.
