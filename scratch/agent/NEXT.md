# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s651 recap (read this first)

**s650 freeroll consumed — Outcome B + H-adlb-writer REFUTED:**
- outer rc=137 600s mid-att6
- att3 recovery-active: recov768 LIVE thr11d_new=1
  - arm_freelist@146070ms 0x2/0x60 LIVE
  - freelist to_zero #2 @165421ms prev_f=0x2 prev_sz=0x60
  - **adlb_n=358 adlb_tgt=0 adlb_near=0** → ADLB never touches header
  - flz_fault_hdr=0 late=0; ~15s quiet fault_n=55 then +8 around stomp
  - tz_corr last_sym=**submitSceneNodeRender** last_in_hdr=0 last_fa=+0x40
  - CRASH coalesceFreeHeapBlocks (not fail136c this hold)
- Rate-limit hole: after arm_fl only n≤32 logged; n=33..63 dropped

**Landed s651 fault_ring + near_hdr** in `src/main/main.cpp`:
- 16-slot ring always records every page fault (no BT)
- freelist to_zero dumps `event=fault_ring` (last 16)
- near_hdr (fa in [host,host+0x80)) always logs line (no BT)
- heartbeat `ring_w=`
- Posctrl 70s: CRASH=0 fault_n≥8 ring_w tracks fault_n

**Queued:** `scratch/agent/soak_queue/s651_fl_fault_ring_freeroll.sh`

## This iteration's work unit

**Primary: consume s651 freeroll SOAK-RESULTS (or run if still queued).**

1. Posctrl already LIVE (ring_w / fault lines / CRASH=0)
2. Prefer **recovery-active** (`recov768≥1`) with `arm_fl≥1`
3. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60`
4. Discriminators:
   - **A)** `event=fault_ring` with `in_hdr=1` → names store leaf (sym+off);
     next session guards or instruments that site only
   - **B)** ring last entries `near_hdr=1` / named leaf just before zero
     → RW-race window writer; instrument that leaf
   - **C)** freelist to_zero but ring empty / ring_w=0 → ring path failed
   - **D)** ring all far-page thrash (in_hdr=0 near_hdr=0) → pure RW-race
     with no near-header signal; pivot to store census / bulk-clear audit
   - Passive: thr11d_new, fail136c, late/CRASH, adlb_tgt (expect 0)
5. If A/B names a specific sym+off, next session is leaf probe only

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
| H-fault-writer | mprotect names freelist stomp leaf | flz_fault_hdr≥1 ∧ flz_fault_sym | ACTIVE (B s646/s650/s651; C s647/s648) |
| H-ss-rearm | ARM64 SS from SEGV closes race | ss_rearm≥1 ∧ CRASH=0 | **REFUTED s647** |
| H-busy-rearm | 20µs busy re-arm catches header store | freelist to_zero ∧ flz_fault_hdr≥1 | **REFUTED s650** freelist-class |
| H-recov-co-gate-stomp | freelist 0x2/0x60→0 needs recovery-active | silent arm_fl ∧ no fl-to_zero vs recov+fl-to_zero | **SUPPORTED s648/s650/s651** |
| H-bt-thrash-toxic | BT-every-fault self-DOS under want=2 | ~7.5k BT dumps measured | **CONFIRMED s648** |
| H-perturb-from-BT | BT thrash elevates recovery silence | rate-limit freeroll still silent | **REFUTED s649** |
| H-mprotect-concurrent-CRASH | armed==0 + fa on page → old handler CRASH | s648 att4 SIGBUS | **CONFIRMED s649** |
| H-late-recover | want!=0 recover closes concurrent CRASH | arm_fl + no post-arm CRASH | **SUPPORTED soft s650** |
| H-adlb-writer | allocateDisplayListBuffer zeros freelist hdr | adlb TARGET ∧ freelist to_zero | **REFUTED s651** freelist-class |
| H-fault-ring-names | ring dump at freelist to_zero names stomp leaf | fault_ring in_hdr/near_hdr + sym | ACTIVE (posctrl ring_w LIVE) |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Retry ARM64 SS / thread_set_state from SEGV (REFUTED s647)
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop; dms REFUTED it)
- Treat guest_pc=rs_memset return-nop alone as dest proof without msfl hit=1
- Treat H-memset-writer as open for freelist class (REFUTED s646)
- Treat H-busy-rearm as still-evaluable for freelist (REFUTED s650)
- Treat H-adlb-writer as open for freelist class (REFUTED s651)
- Treat last_sym=allocateDisplayListBuffer or submitSceneNodeRender alone as
  writer proof without in_hdr/near_hdr ring entry or TARGET co-timed
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
`[fl-zero-fault] event=fault_ring`, `near_hdr=`, `ring_w=`, `[adlb-fl-stomp]`,
`to_zero_correlate`, `[fl-zero-poll]`, `[memset-fl-dest]`, `[drain-mesh-stomp]`,
`0x801F3CC0`, `0x1F3CC0`, fail136c, thr11d_new, -391, -395, -404, -405
