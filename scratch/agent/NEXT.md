# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s649 recap (read this first)

**s648 freeroll consumed — Outcome C + mprotect concurrent CRASH:**
- outer rc=137 600s mid-att5; 0 recovery-active (att1 mat3inv, att4 silent)
- att4: **arm_freelist@146s 0x2/0x60 LIVE** then **immediate SIGBUS**
  si_addr=0x3001f23b4 (same 16KB page as slot 0x1F3CC0) in
  buildModelViewerTextPage — old handler required armed==1; peer/stale-TLB
  fault after first neighbor disarm returned false → [CRASH]
- Rate-limit worked (fault lines ~23–32 not ~7.5k)
- No freelist-shaped to_zero; H-busy-rearm / H-fault-writer unevaluable
- **H-perturb-from-BT REFUTED** (silent under rate-limit AND under full BT)

**Landed s649 late-recover** (`fl_zero_try_handle_fault`):
- recover watch-page faults when want!=0 even if armed==0
- log late=1; heartbeat fault_late=
- Posctrl 55s: fault_n LIVE late= field CRASH=0

**Queued:** `scratch/agent/soak_queue/s649_fl_late_recover_freeroll.sh`

## This iteration's work unit

**Primary: consume s649 freeroll SOAK-RESULTS (or run if still queued).**

1. Posctrl: `flz_fault_n≥1` (boot-zero) — instrument not cold
2. Prefer **recovery-active** attempts (`recov768≥1`) with `arm_fl≥1`
3. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60`
4. Discriminators:
   - **A)** `flz_fault_hdr≥1` near freelist to_zero + sym names recomp leaf
     → instrument that leaf only for zero-store of flags/size
   - **A2)** `to_zero_correlate last_in_hdr=1` or last_sym names leaf
   - **B)** arm_fl + freelist to_zero + flz_fault_hdr=0 still
     → 20µs race residual; escalate header-byte watch / leaf probes
   - **C)** recovery-active + arm_fl + no freelist to_zero
     → requeue once OR escalate; silent-only is **not** Outcome B
   - **E)** arm_fl + want=2 + `late≥1` + no post-arm [CRASH] in
     buildModelViewerTextPage → late-recover LIVE (closes s648 att4 class)
   - **F)** arm_fl then SIGBUS/CRASH again in buildModelViewerTextPage
     → late-recover insufficient; **disable want=2 mprotect** and escalate
     to non-page watch (poller-only + targeted leaf probes)
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
| H-fault-writer | mprotect names freelist stomp leaf | flz_fault_hdr≥1 ∧ flz_fault_sym | ACTIVE (B s646; C s647/s648) |
| H-ss-rearm | ARM64 SS from SEGV closes race | ss_rearm≥1 ∧ CRASH=0 | **REFUTED s647** |
| H-busy-rearm | 20µs busy re-arm catches header store | freelist to_zero ∧ flz_fault_hdr≥1 | ACTIVE (uneval s647–s648) |
| H-recov-co-gate-stomp | freelist 0x2/0x60→0 needs recovery-active | silent arm_fl ∧ no fl-to_zero vs recov+fl-to_zero | **SUPPORTED s648** |
| H-bt-thrash-toxic | BT-every-fault self-DOS under want=2 | ~7.5k BT dumps measured | **CONFIRMED s648** |
| H-perturb-from-BT | BT thrash elevates recovery silence | rate-limit freeroll still silent | **REFUTED s649** |
| H-mprotect-concurrent-CRASH | armed==0 + fa on page → old handler CRASH | s648 att4 SIGBUS | **CONFIRMED s649** |
| H-late-recover | want!=0 recover closes concurrent CRASH | arm_fl + late≥1 + no post-arm CRASH | ACTIVE (posctrl only) |
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
- Score Outcome B from recovery-silent-only freerolls
- Re-enable full BT on every want==2 fault (toxic measured s647)
- Re-open H-perturb-from-BT for silence elevation (REFUTED s649)

### Reference tags
`[fl-zero-fault]`, `late=`, `busy_rearm`, `to_zero_correlate`, `[fl-zero-poll]`,
`[fl-zero-poll-bt]`, `[fl-zero-poll-gbt]`, `[memset-fl-dest]`,
`[drain-mesh-stomp]`, `[fl-hdr-write]`, `[fl-zero-watch]`,
`0x801F3CC0`, `0x1F3CC0`, BREADCRUMB19, fail136c, thr11d_new, -391, -395,
-397, -398, -399, -400, -401, -402, -403
