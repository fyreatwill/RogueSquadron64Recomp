# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s652 recap (read this first)

**s651 freeroll consumed — Outcome B refined; H-ssnr380-writer REFUTED:**
- att1 recovery-active: recov768 LIVE thr11d_new=1 fail136c corrupt
- arm_freelist@146679ms 0x2/0x60; freelist to_zero #2 @166030ms
- **fault_ring LIVE** n=16 inhdr=0 near=9
- last near leaf: `submitSceneNodeRender+0x380` guest=`0x80010054`
  `sw $v0, 0x30($s4)` fa=hdr+0x40 ⇒ s4=user_ptr of LIVE flags=0x2 alloc
  → **payload traffic, NOT header zero** (flags=0x2 means allocated)
- ring also: heapFreeListDequeue near +0x50/+0x64; copyToRAM@phys 0x1F0D74
- adlb_tgt=0 reconfirm; crash do_rom_read (-387 now 5×)

**Landed s652 probes:**
- `[ssnr-hdr-zero]` — 48 zero-stores (off 0/4) in submitSceneNodeRender
- `[fb-fl-writeback]` — copyNativeToRAM range vs phys 0x1F3CC0
- Posctrl 70s: ssnr=182/0 fb=24/0 CRASH=0 ring_w LIVE
- apply: `tools/apply_s652_ssnr_hdr_zero.py`; lib rt64 exported

**Queued:** `scratch/agent/soak_queue/s652_ssnr_fb_fl_stomp_freeroll.sh`

## This iteration's work unit

**Primary: consume s652 freeroll SOAK-RESULTS (or run if still queued).**

1. Posctrl already LIVE (ssnr sample + fb sample + CRASH=0)
2. Prefer **recovery-active** (`recov768≥1`) with `arm_fl≥1`
3. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60`
4. Discriminators:
   - **A)** `ssnr_tgt≥1` TARGET co-timed with freelist to_zero → SSNR
     list-unlink zeros header; next session guards that site only
   - **B)** `fb_hit≥1` range covers 0x1F3CC0 co-timed → host FB writeback
     stomps heap; clamp/skip or refuse wild FB
   - **C)** freelist to_zero with ssnr_tgt=0 and fb_hit=0 → both clean;
     next = heapFreeListDequeue leaf probe or bulk-clear census
   - Passive: thr11d_new, fail136c, fault_ring, adlb_tgt (expect 0)
5. If A/B names a specific site, next session is leaf guard only

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
| H-fault-writer | mprotect names freelist stomp leaf | flz_fault_hdr≥1 ∧ flz_fault_sym | ACTIVE (B race; in_hdr=0 all freerolls) |
| H-ss-rearm | ARM64 SS from SEGV closes race | ss_rearm≥1 ∧ CRASH=0 | **REFUTED s647** |
| H-busy-rearm | 20µs busy re-arm catches header store | freelist to_zero ∧ flz_fault_hdr≥1 | **REFUTED s650** freelist-class |
| H-recov-co-gate-stomp | freelist 0x2/0x60→0 needs recovery-active | silent arm_fl ∧ no fl-to_zero vs recov+fl-to_zero | **SUPPORTED s648/s650/s651** |
| H-bt-thrash-toxic | BT-every-fault self-DOS under want=2 | ~7.5k BT dumps measured | **CONFIRMED s648** |
| H-perturb-from-BT | BT thrash elevates recovery silence | rate-limit freeroll still silent | **REFUTED s649** |
| H-mprotect-concurrent-CRASH | armed==0 + fa on page → old handler CRASH | s648 att4 SIGBUS | **CONFIRMED s649** |
| H-late-recover | want!=0 recover closes concurrent CRASH | arm_fl + no post-arm CRASH | **SUPPORTED soft s650** |
| H-adlb-writer | allocateDisplayListBuffer zeros freelist hdr | adlb TARGET ∧ freelist to_zero | **REFUTED s651** freelist-class |
| H-fault-ring-names | ring dump at freelist to_zero names stomp leaf | fault_ring in_hdr/near_hdr + sym | LIVE ring; near leaf not writer |
| H-ssnr380-writer | SSNR+0x380 / 0x80010054 zeros freelist hdr | fa in_hdr ∨ dest in [hdr,hdr+8) | **REFUTED s652** (payload of LIVE alloc) |
| H-ssnr-zero-stores | SSNR sw$zero 0/4($reg) zeros freelist hdr | ssnr TARGET ∧ freelist to_zero | ACTIVE (posctrl LIVE) |
| H-fb-writeback-stomp | RT64 copyNativeToRAM covers phys 0x1F3CC0 | fb HIT ∧ freelist to_zero | ACTIVE (posctrl LIVE; ring had copyToRAM@0x1F0D74) |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Retry ARM64 SS / thread_set_state from SEGV (REFUTED s647)
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop; dms REFUTED it)
- Treat guest_pc=rs_memset return-nop alone as dest proof without msfl hit=1
- Treat H-memset-writer as open for freelist class (REFUTED s646)
- Treat H-busy-rearm as still-evaluable for freelist (REFUTED s650)
- Treat H-adlb-writer as open for freelist class (REFUTED s651)
- Treat submitSceneNodeRender+0x380 / 0x80010054 as header-writer proof
  (REFUTED s652 — payload of LIVE 0x2/0x60 alloc)
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
- Treat near_hdr alone as writer ID without dest in [hdr,hdr+8)

### Reference tags
`[ssnr-hdr-zero]`, `[fb-fl-writeback]`, `[fl-zero-fault] event=fault_ring`,
`near_hdr=`, `ring_w=`, `[adlb-fl-stomp]`, `to_zero_correlate`,
`[fl-zero-poll]`, `[memset-fl-dest]`, `[drain-mesh-stomp]`,
`0x801F3CC0`, `0x1F3CC0`, `0x80010054`, fail136c, thr11d_new, -391, -405, -406
