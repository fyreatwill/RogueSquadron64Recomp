# NEXT work unit

HYPOTHESIS-ID: alloc-tail-walk-guard

## s561 recap (read this first)

**Opened item -343: residual freelist initial-deref GUARD2 (alloc-tail family), 1st live-verify CLEAN.**

After s560 closed residual walk GUARD3+GUARD4 (1/2), residual init-deref audit of the same 97
walk sites found:
- **92** unguarded `lw $v0, 0x0($aN)` → `ctx->r2 = MEM_W(ctx->rN, 0X0)` after null-check
- **5** already covered by drainMesh head guards (s363) — excluded
- Host regs: r4×78, r5×11, r7×3 (mips a0/a1/a3)
- Applied GUARD2 x92 (`ROGUESQ_LOG_ALLOC_TAIL_GUARD2`)

**1st live-verify:** hangarbay n=2700, full ~300s rc=0, 0 fires, 0 CRASH. True-negative baseline.

**Folded confirms:**
- Item **-341 FULLY CLOSED 2/2** (s560 freelist_walk_guard4_confirm_retry: hangarbay n=2900,
  full 300s, 0 fires) — covers -339/-337.
- Item **-342** confirm WEAK again (hangarbay n=4, item -306) — discarded; retry re-queued.

**Queued:**
- `scratch/agent/soak_queue/s561_alloc_tail_guard2_confirm.sh` (item -343 2nd confirm)
- `scratch/agent/soak_queue/s561_alloc_tail_guard34_confirm_retry.sh` (item -342 2nd confirm)

## This iteration's work unit

**Fold in s561 confirms from SOAK-RESULTS:**

1. If `s561_alloc_tail_guard2_confirm` CLEAN (hangarbay double-digit+, 0 regression): mark item
   -343 FULLY CLOSED 2/2.
2. If `s561_alloc_tail_guard34_confirm_retry` CLEAN: mark item -342 FULLY CLOSED 2/2. If WEAK
   again (item -306, hangarbay n<10): discard+re-queue once more (or escalate if 3rd weak in a
   row suggests a real recipe problem).

**Then pick next M3 class:**

### Option A — packing DL-cursor residual (item -317 DEFERRED)
Shape-mismatched packing: write base is DL cursor; freelist reload branch-only. Separate class
from freelist-node write / walk guards.

### Option B — multi-occurrence breadcrumb escalation
Items -332 (2 occ, moderate), -330 (2 weak). Only escalate on a 3rd independent occurrence.

### Option C — residual scan after GUARD2 closes
Re-run walk/init-deref residual enum; expect empty if family fully closed.

### Hypotheses (for Option A if taken)
1. **H1:** packing DL-cursor sites have a single guardable shape and catch live corruption.
2. **H2:** packing is compare-only / non-pointer and should stay DEFERRED.
3. **H3:** packing sites already covered by sibling/DL-list families.

### Discriminating measurement
Tracer or grep enum of packing residual; classify write-through vs branch-only; apply only if
write-through with freelist-derived base.

### Exact commands
```bash
git log --oneline -3
tail -8 scratch/agent/SOAK-RESULTS.md
# Fold confirms first; if -343 and -342 CLOSED 2/2, Option A packing or Option B/C
```

Do NOT re-open freelist-node rN/0X0, classic r2/0X4, or freelist-walk GUARD4 (-341) — all FULLY
CLOSED. Do NOT re-open item -343 sites once 2/2 closed.

## Iron-rule reminders
- Confirm free session number at START before naming.
- Weak early deaths on item -306 `setByteAcrossEntryList+176`/`0x800aafa8` with hangarbay n<10:
  discard+retry (s548-s561 standing gotcha).
- Never trust 0-fires without double-digit+ hangarbay-entry.
- Kill with SIGKILL; run from build/ with ROM.
- Full guard table: docs/PROJECT-OVERVIEW.md §22-§26.
