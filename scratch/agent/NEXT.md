# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s648 recap (read this first)

**s647 freeroll consumed — Outcome C (not B):**
- 2× recovery_silent; outer rc=137 600s mid-att3
- arm_freelist@~145s f=0x2/sz=0x60 LIVE both; heartbeats 150–195s
  flags=0x2 size=0x60 fault_armed=1 want=2 — **header survived ~50s**
- **no freelist-shaped to_zero** (only menu 0x8E8E→0 @t≈51s)
- SCORE: flz_fault_n≈7500 flz_fault_hdr=0 flz_fault_arm_fl=1
  flz_busy_rearm=9–10 (log-capped; heartbeats 106–124) flz_tz_corr=0
- **H-busy-rearm unevaluable** (needs freelist to_zero)

**H-recov-co-gate-stomp SUPPORTED (dual-source):**
- freelist 0x2/0x60→0 co-occurs with recovery-active freerolls
  (s646 att3 recov768=7956 freelist#2; s645 recov768=1 freelist#2)
- absent on recovery-silent + arm_fl holds (s647×2; s646 att1 arm_fl=1
  menu-only to_zero)

**BT thrash toxic (measured s647 want=2):**
- ~7500 faults all in_hdr=0 (buildModelViewerTextPage page-neighbor)
- BT on every fault → ~121k frame lines / ~24 MB after arm_freelist
- H-perturb open: may elevate recovery silence / block freelist stomp

**Landed s648 rate-limit** (`fl_zero_try_handle_fault`):
- line: first 32 / all in_hdr / every 256th want==2 non-hdr
- BT: first 16 / all in_hdr cap32 / every 256th want==2
- Posctrl 55s: fault_n=25 CRASH=0 BT frames=320 (first-16 only)

**Queued:** `scratch/agent/soak_queue/s648_fl_bt_ratelimit_freeroll.sh`

## This iteration's work unit

**Primary: consume s648 freeroll SOAK-RESULTS (or run if still queued).**

1. Posctrl: `flz_fault_n≥1` (boot-zero) — instrument not cold
2. Prefer **recovery-active** attempts (`recov768≥1`) with `arm_fl≥1`
3. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60`
4. Discriminators on freelist window / to_zero:
   - **A)** `flz_fault_hdr≥1` near freelist to_zero with `flz_fault_sym` naming
     a recomp leaf → instrument that leaf only for zero-store of flags/size
   - **A2)** `to_zero_correlate last_in_hdr=1` or last_sym names leaf even if
     SCORE hdr lag → treat as A for next session
   - **B)** arm_fl≥1 + freelist to_zero + flz_fault_hdr=0 still
     → 20µs race not closed; escalate to header-byte watch (not page
     mprotect) or targeted leaf probes from freelist-window neighbors
   - **C)** no freelist to_zero after ≥1 recovery-active + arm_fl attempt
     → requeue once OR escalate; silent-only is **not** Outcome B
   - **D)** recovery-active rate vs s647 (2/2 silent): if still all silent
     under rate-limit → H-perturb-from-BT REFUTED (silence not BT-caused);
     if recovery appears and freelist to_zero returns → H-perturb-from-BT
     SUPPORTED and busy_rearm re-testable
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
| H-fault-writer | mprotect names freelist stomp leaf | flz_fault_hdr≥1 ∧ flz_fault_sym | ACTIVE (B s646; C s647) |
| H-ss-rearm | ARM64 SS from SEGV closes race | ss_rearm≥1 ∧ CRASH=0 | **REFUTED s647** |
| H-busy-rearm | 20µs busy re-arm catches header store | freelist to_zero ∧ flz_fault_hdr≥1 | ACTIVE (uneval s647) |
| H-recov-co-gate-stomp | freelist 0x2/0x60→0 needs recovery-active | silent arm_fl ∧ no fl-to_zero vs recov+fl-to_zero | **SUPPORTED s648** |
| H-bt-thrash-toxic | BT-every-fault self-DOS under want=2 | ~7.5k BT dumps measured | **CONFIRMED s648** |
| H-perturb-from-BT | BT thrash elevates recovery silence / blocks stomp | rate-limit freeroll recov rate vs s647 | ACTIVE |
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
- Score Outcome B from recovery-silent-only freerolls (s648: no freelist to_zero)
- Re-enable full BT on every want==2 fault (toxic measured s647)

### Reference tags
`[fl-zero-fault]`, `busy_rearm`, `to_zero_correlate`, `[fl-zero-poll]`,
`[fl-zero-poll-bt]`, `[fl-zero-poll-gbt]`, `[memset-fl-dest]`,
`[drain-mesh-stomp]`, `[fl-hdr-write]`, `[fl-zero-watch]`,
`0x801F3CC0`, `0x1F3CC0`, BREADCRUMB19, fail136c, thr11d_new, -391, -395,
-397, -398, -399, -400, -401, -402
