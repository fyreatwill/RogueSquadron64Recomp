# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s650 recap (read this first)

**s649 freeroll consumed — Outcome B + H-busy-rearm REFUTED:**
- outer rc=137 600s mid-att2 HOLD (att2 recovery-active, no SCORE line)
- att1: recovery_silent; menu to_zero only; arm_fl=1 on SCORE
- att2: recov768 LIVE; **arm_freelist@145991ms 0x2/0x60 LIVE**
  - freelist **to_zero #2 @165335ms** prev_f=0x2 prev_sz=0x60
  - flz_fault_hdr=0 fault_late=0 CRASH=0
  - heartbeats 150–165s: armed=1 fault_n stuck **49** then silent zero
    (~15s gap) → **H-busy-rearm REFUTED freelist-class**
  - to_zero_correlate last_sym=**allocateDisplayListBuffer** last_in_hdr=0
    last_fa=+0x50 (weak; not dual-source writer proof)
  - thr11d_new=0 (id=11 live); zero_node@0x801F3CC0 prev=0x801ED1B0
- H-late-recover soft-E (no post-arm CRASH); H-recov-co-gate-stomp reconfirmed

**Landed s650 `[adlb-fl-stomp]`** on allocateDisplayListBuffer stores
(tools/apply_s650_adlb_fl_stomp.py, 10 sites). Posctrl 55s: adlb_n=123
TARGET=0 CRASH=0 fault_n=24.

**Queued:** `scratch/agent/soak_queue/s650_adlb_fl_stomp_freeroll.sh`

## This iteration's work unit

**Primary: consume s650 freeroll SOAK-RESULTS (or run if still queued).**

1. Posctrl: `adlb_n≥1` sample lines (boot ADLB traffic)
2. Prefer **recovery-active** (`recov768≥1`) with `arm_fl≥1`
3. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60`
4. Discriminators:
   - **A)** `[adlb-fl-stomp] TARGET` co-timed with freelist to_zero
     → H-adlb-writer CONFIRMED; site= names store for guard/fix
   - **B)** freelist to_zero + adlb TARGET=0
     → ADLB not header writer; next leaf (correlate or store census)
   - **C)** recovery-active + arm_fl + no freelist to_zero
     → requeue once; silent-only is not B
   - Passive: late/CRASH recurrence (E/F from s649)
5. If A fires with a specific site, next session guards or narrows that site only

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
| H-fault-writer | mprotect names freelist stomp leaf | flz_fault_hdr≥1 ∧ flz_fault_sym | ACTIVE (B s646/s650; C s647/s648) |
| H-ss-rearm | ARM64 SS from SEGV closes race | ss_rearm≥1 ∧ CRASH=0 | **REFUTED s647** |
| H-busy-rearm | 20µs busy re-arm catches header store | freelist to_zero ∧ flz_fault_hdr≥1 | **REFUTED s650** freelist-class |
| H-recov-co-gate-stomp | freelist 0x2/0x60→0 needs recovery-active | silent arm_fl ∧ no fl-to_zero vs recov+fl-to_zero | **SUPPORTED s648/s650** |
| H-bt-thrash-toxic | BT-every-fault self-DOS under want=2 | ~7.5k BT dumps measured | **CONFIRMED s648** |
| H-perturb-from-BT | BT thrash elevates recovery silence | rate-limit freeroll still silent | **REFUTED s649** |
| H-mprotect-concurrent-CRASH | armed==0 + fa on page → old handler CRASH | s648 att4 SIGBUS | **CONFIRMED s649** |
| H-late-recover | want!=0 recover closes concurrent CRASH | arm_fl + no post-arm CRASH | **SUPPORTED soft s650** (late=0 this run) |
| H-adlb-writer | allocateDisplayListBuffer zeros freelist hdr | adlb TARGET ∧ freelist to_zero | ACTIVE (posctrl samples only) |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Retry ARM64 SS / thread_set_state from SEGV (REFUTED s647)
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop; dms REFUTED it)
- Treat guest_pc=rs_memset return-nop alone as dest proof without msfl hit=1
- Treat H-memset-writer as open for freelist class (REFUTED s646)
- Treat H-busy-rearm as still-evaluable for freelist (REFUTED s650)
- Treat last_sym=allocateDisplayListBuffer alone as writer proof without
  adlb TARGET co-timed with freelist to_zero
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
`[adlb-fl-stomp]`, `[fl-zero-fault]`, `late=`, `busy_rearm`, `to_zero_correlate`,
`[fl-zero-poll]`, `[fl-zero-poll-bt]`, `[fl-zero-poll-gbt]`, `[memset-fl-dest]`,
`[drain-mesh-stomp]`, `[fl-hdr-write]`, `[fl-zero-watch]`,
`0x801F3CC0`, `0x1F3CC0`, BREADCRUMB19, fail136c, thr11d_new, -391, -395,
-397, -398, -399, -400, -401, -402, -403, -404
