# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s647 recap (read this first)

**s646 freeroll consumed — Outcome B (mprotect race):**
- att3 freelist to_zero #2 t=164873 phys=0x1F3CC0 prev_f=0x2 prev_sz=0x60
- arm_freelist@t=145570; heartbeats 150–160s fault_armed=1 fault_n=20
- freelist-window faults n=18–21 **all in_hdr=0**
  (buildModelViewerTextPage, submitSceneNodeRender fa=hdr+64, n=21 garbage PC)
- n=21 co-timed with to_zero → **250µs poller re-arm race** after neighbor thrash
- SCORE: flz_fault_n=21 flz_fault_hdr=0 flz_fault_arm_fl=1 flz_fault_sym=none
- **H-fault-writer still open** (missed leaf; not refuted)

**SS rearm REFUTED (do not retry):**
- `thread_set_state(ARM_DEBUG_STATE64)` from SEGV → nested SIGTRAP in
  `mach_msg`/`thread_set_state` → CRASH path (posctrl CRASH=36, ss_rearm=0)

**Landed busy_rearm (Outcome B fix):**
- want=1 boot / want=2 freelist
- freelist-only busy re-arm spinner, ≥20µs hold-off after last fault
- freelist poller sleep 10µs; full BT while want==2; to_zero_correlate
- **Posctrl 55s:** arm_boot, fault_n=15, CRASH=0 (busy_rearm=0 under want=1 OK)

**Queued:** `scratch/agent/soak_queue/s647_fl_busy_rearm_freeroll.sh`
(SCORE: flz_fault_* + flz_busy_rearm + flz_tz_corr + flz_tz_corr_inhdr)

## This iteration's work unit

**Primary: consume s647 freeroll SOAK-RESULTS (or run if still queued).**

1. Posctrl: `flz_fault_n≥1` (boot-zero) — instrument not cold
2. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60`
3. Require `flz_fault_arm_fl≥1` and preferably `flz_busy_rearm≥1` after arm
4. Discriminators on freelist window / to_zero:
   - **A)** `flz_fault_hdr≥1` near freelist to_zero with `flz_fault_sym` naming
     a recomp leaf → instrument that leaf only for zero-store of flags/size
   - **A2)** `to_zero_correlate last_in_hdr=1` or last_sym names leaf even if
     SCORE hdr lag → treat as A for next session
   - **B)** arm_fl≥1 + freelist to_zero + flz_fault_hdr=0 still
     → 20µs race not closed; escalate to per-thread ARM watchpoint on header
     bytes only (not page mprotect), or log-only correlate + targeted leaf
     probes from freelist-window BT neighbors (submitSceneNodeRender family)
   - **C)** no freelist to_zero → requeue freeroll once
5. If A/A2 fires with a specific leaf, next session instruments that leaf only

## Hypotheses

| ID | Claim | Discriminator | Status |
|----|-------|---------------|--------|
| H-ltexmg1 | guard LIVE | ltexmg≥1 ∧ ltex_null=0 | CONFIRMED |
| H-walk1 | S32 MEM_* | posctrl sane | CONFIRMED s626 |
| H-E8-corrupt | zero-node mid E8 | raw @0x801F3CC0 | CONFIRMED s638 |
| H-zero-free | free zeros header | fl-hdr-write size=0 | **REFUTED s639** |
| H-split-bug | split size=0 residual | fl-hdr-write split size=0 | **REFUTED s639** |
| H-oob-store | external stomp of valid header | to_zero 0x2/0x60→0 | **CONFIRMED s640** |
| H-walk-into-zeros | prev size wrong → land on zeros | prev_sz too small | **REFUTED s640** |
| H-drainmesh-stomp | drainMesh sw$zero stomps headers | [drain-mesh-stomp]@0x801F3CC0 | **REFUTED s642** |
| H-hostbt-writer | poller BT names real store path | [fl-zero-poll-bt] recomp leaf | **REFUTED s643** |
| H-gbt-writer | game-thread BT names store path | freelist gbt store leaf | **REFUTED s645** freelist-class |
| H-bc19-live | freelist stamps update sticky PC | menu to_zero pc in rs_* | **CONFIRMED s645** |
| H-memset-writer | rs_memset zeros freelist header | msfl hit@0x801F3CC0 ∧ freelist to_zero | **REFUTED s646** freelist-class |
| H-fault-writer | mprotect names freelist stomp leaf | flz_fault_hdr≥1 ∧ flz_fault_sym | ACTIVE (B s647) |
| H-ss-rearm | ARM64 SS from SEGV closes race | ss_rearm≥1 ∧ CRASH=0 | **REFUTED s647** |
| H-busy-rearm | 20µs busy re-arm catches header store | freelist to_zero ∧ flz_fault_hdr≥1 | ACTIVE |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Retry ARM64 SS / thread_set_state from SEGV (REFUTED s647)
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop; dms REFUTED it)
- Treat guest_pc=rs_memset return-nop alone as dest proof without msfl hit=1
- Treat H-memset-writer as open for freelist class (REFUTED s646)
- Expect poller `backtrace()` / gbt to name a short freelist store
- Soft-skip thr12 / coalesce past zero nodes without writer ID
- Re-open H-drainmesh-stomp / H-zero-free / H-split / H-walk-into-zeros without
  new counterexample
- Raise HOLD_S past 210
- Spend session on pure thr11d rate soaks
- Merge -385 with -387/-384/-373/-386
- uint32 KSEG0 MEM bases (use S32)
- Use re.sub *string* replacement for C probes containing `\n` in format
  strings (use lambda repl — s641 lesson)
- Try ROGUESQ_HWBP on macOS (prints "not supported")

### Reference tags
`[fl-zero-fault]`, `busy_rearm`, `to_zero_correlate`, `[fl-zero-poll]`,
`[fl-zero-poll-bt]`, `[fl-zero-poll-gbt]`, `[memset-fl-dest]`,
`[drain-mesh-stomp]`, `[fl-hdr-write]`, `[fl-zero-watch]`,
`0x801F3CC0`, `0x1F3CC0`, BREADCRUMB19, fail136c, thr11d_new, -391, -395,
-397, -398, -399, -400, -401
