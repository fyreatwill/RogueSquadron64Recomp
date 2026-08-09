# NEXT work unit

HYPOTHESIS-ID: freelist-walk-guard4

## s559 recap (read this first)

**Opened item -341: freelist-walk GUARD4 (16 sites), 1st live-verify CLEAN.**

Source discrimination (H1 confirmed): after existing GUARD3 does `v1 = *v1`, next insn peeks
`v0 = *v1` on the freshly-loaded NEW pointer with zero validation — heapWalker s218 GUARD4 gap.
Sites with GUARD3 but no GUARD4:
- emitAllocatedDLCommand x3 (incl item -339 @0x800088EC) — FIXED
- heapFreeListDequeue x4 — FIXED
- submitSceneNodeRender x9 (incl item -337 @0x80010DF4 + s123 first @0x80010178) — FIXED
- heapWalker: already had GUARD4 (s218)

Env: `ROGUESQ_LOG_EMIT_DL_GUARD4` / `HEAPLISTDEQ_GUARD4` / `SCENE_NODE_LIST_GUARD4`.

**1st live-verify (after discarding weak item -306 draw):** hangarbay n=2900, full ~300s rc=0,
0 fires on all 16 new guards, 0 CRASH. True-negative baseline (intermittent corruption).

**2nd confirm queued:** `scratch/agent/soak_queue/s559_freelist_walk_guard4_confirm.sh`
(loop will run between iterations).

## This iteration's work unit

**Fold in s559 confirm if present in SOAK-RESULTS; if CLEAN mark item -341 FULLY CLOSED 2/2
(and -339/-337 CLOSED with it). Then pick next M3 class:**

### Option A (if confirm CLEAN) — residual freelist-walk sites WITHOUT GUARD3
~93 `v1=*v1; v0=*v1` sites in funcs_3/4 with no GUARD3 at all (emitFrameRdpInitDl,
beginFrameDLChunk, renderLitMeshFaceGroup, etc.). Classify: true freelist walk vs packing
false-positive. Fix only shape-matched freelist walks as GUARD3+GUARD4 pairs (or combined).

### Option B — multi-occurrence breadcrumb escalation
Items -332 (2 occ, moderate), -330 (2 weak), others single. Only escalate if a 3rd independent
occurrence appears in SOAK-RESULTS.

### Option C — packing DL-cursor audit (item -317 DEFERRED residual)
Separate class: write base is DL cursor; freelist reload branch-only.

### Hypotheses (for Option A if taken)
1. **H1:** some of the 93 are true freelist walks missing both GUARD3 and GUARD4.
2. **H2:** all 93 are packing / non-freelist and should stay DEFERRED.
3. **H3:** a subset matches freelist shape but already covered by another family (GENERIC_CACHE, etc.).

### Discriminating measurement
Grep-enumerate the 93; for each, check whether the walk pointer comes from freelist global
0x801163B0 / findAndUnlinkSmallestEntry vs s0 DL packing. Only freelist-origin sites are candidates.

### Exact commands (start here if confirm already folded)
```bash
git log --oneline -3
# Fold confirm first
tail -5 scratch/agent/SOAK-RESULTS.md
# If confirm CLEAN: mark -341 2/2, then residual scan
python3 - <<'PY'
# re-scan GUARD4-shape sites lacking any loop-back guard (see s559 NEXT analysis)
PY
```

Do NOT re-open freelist-node rN/0X0 or classic r2/0X4 — both residual-empty and FULLY CLOSED.
Do NOT re-open item -341 sites once 2/2 closed.

## Iron-rule reminders
- Confirm free session number at START before naming.
- Weak early deaths on item -306 `setByteAcrossEntryList+176`/`0x800aafa8` with hangarbay n<10:
  discard+retry (s548-s553 standing gotcha).
- Never trust 0-fires without double-digit+ hangarbay-entry.
- Kill with SIGKILL; run from build/ with ROM.
- Full guard table: docs/PROJECT-OVERVIEW.md §22-§25.
