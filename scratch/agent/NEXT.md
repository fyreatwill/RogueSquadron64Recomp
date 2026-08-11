# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s654 recap (read this first)

**s653 freeroll consumed — Outcome A CONFIRMED (H-fb-skip-stops-stomp):**
- att2 + att3 engaged recovery-silent (recov768=0 both): dual-source
- arm_freelist @146–147s phys 0x1F3CC0 f=0x2 sz=0x60 LIVE both
- **SKIP_WILD_W exact killer CIMG** `addr=0x1F0D74 w=1161 siz=3 rows=0..277`
  (identical to s652 freeroll `[fb-fl-writeback] HIT` that stomped freelist
  @165665ms) — fires in historical ~165–170s stomp window
- freelist **0x2/0x60 SURVIVED** heartbeats through ~195–200s
- freelist-shaped to_zero=0 (only menu 0x8E8E ~51s)
- skip_wild=40 fb_hit=0 skip_fl=0 both; thr11d_new=0 fail136c=0 (silent path)
- att1 early crash; att4 600s outer cap mid-run (no SCORE)
- Wild CIMG fires on silent → H-recov-co-gate-stomp partly recharacterized
  (recovery not required for killer CIMG emission)

**Product:** `SKIP_WILD_W` + `SKIP_FL_HDR` LIVE-VERIFIED. FB-writeback
freelist-stomp class CLOSED (-407).

**Queued:** `scratch/agent/soak_queue/s654_post_fbskip_pipeline_freeroll.sh`

## This iteration's work unit

**Primary: consume s654 pipeline freeroll SOAK-RESULTS (or run if still queued).**

1. Prefer **recovery-active** (`recov768≥1`) with `arm_fl≥1`
2. Freelist-shaped: confirm no `to_zero` with `prev_f=0x2 prev_sz=0x60`
3. Confirm SKIP of killer still fires: `SKIP_WILD_W` `addr=0x1F0D74 w=1161`
4. Discriminators:
   - **A)** recov768≥1 ∧ arm_fl ∧ no freelist to_zero ∧ thr11d_new=1 ∧
     fail136c=0 → freelist survival unblocks thr11d path (partial pipeline
     SUCCESS). Next: thr12 / null-malloc / class-D path under freelist intact
   - **B)** recov768≥1 ∧ arm_fl ∧ no freelist to_zero ∧ thr11d_new=1 ∧
     fail136c=1 reason=corrupt → residual other zero-node / selected-pool
   - **C)** recov768≥1 ∧ freelist to_zero 0x2/0x60 with skip≥1 → residual
     other writer; re-open ring/near after skip proof
   - **D)** recov768≥1 ∧ freelist to_zero with skip=0 → path leak past
     rs64_writeback_sane
5. Passive: ltexmg, ssnr_tgt (expect 0), fb_hit (expect 0), skip_wild of
   0x1F0D74, ship_store / B8 chain if thr11d fires

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
| H-recov-co-gate-stomp | freelist 0x2/0x60→0 needs recovery-active | silent arm_fl ∧ no fl-to_zero vs recov+fl-to_zero | **PARTLY RECHARACTERIZED s654** (killer CIMG fires on silent too) |
| H-bt-thrash-toxic | BT-every-fault self-DOS under want=2 | ~7.5k BT dumps measured | **CONFIRMED s648** |
| H-perturb-from-BT | BT thrash elevates recovery silence | rate-limit freeroll still silent | **REFUTED s649** |
| H-mprotect-concurrent-CRASH | armed==0 + fa on page → old handler CRASH | s648 att4 SIGBUS | **CONFIRMED s649** |
| H-late-recover | want!=0 recover closes concurrent CRASH | arm_fl + no post-arm CRASH | **SUPPORTED soft s650** |
| H-adlb-writer | allocateDisplayListBuffer zeros freelist hdr | adlb TARGET ∧ freelist to_zero | **REFUTED s651** freelist-class |
| H-fault-ring-names | ring dump at freelist to_zero names stomp leaf | fault_ring in_hdr/near_hdr + sym | LIVE ring; near leaf not writer |
| H-ssnr380-writer | SSNR+0x380 / 0x80010054 zeros freelist hdr | fa in_hdr ∨ dest in [hdr,hdr+8) | **REFUTED s652** (payload of LIVE alloc) |
| H-ssnr-zero-stores | SSNR sw$zero 0/4($reg) zeros freelist hdr | ssnr TARGET ∧ freelist to_zero | **REFUTED s653** freelist-class |
| H-fb-writeback-stomp | RT64 copyNativeToRAM covers phys 0x1F3CC0 | fb HIT ∧ freelist to_zero | **CONFIRMED s653** dual-source |
| H-fb-skip-stops-stomp | SKIP_WILD_W/SKIP_FL_HDR prevents freelist to_zero | arm_fl ∧ no fl-to_zero ∧ skip≥1 | **CONFIRMED s654** dual-source |
| H-fl-survive-unblocks-thr11d | freelist intact under recovery → thr11d∧!fail136c | recov768∧arm_fl∧!fl_to_zero∧thr11d_new∧!fail136c | ACTIVE (queued freeroll) |
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
- Treat H-ssnr-zero-stores as open for freelist class (REFUTED s653)
- Treat H-fb-writeback-stomp / H-fb-skip-stops-stomp as open without new
  counterexample (CONFIRMED s653/s654; class CLOSED)
- Treat last_sym=allocateDisplayListBuffer or submitSceneNodeRender alone as
  writer proof without in_hdr/near_hdr ring entry or TARGET co-timed
- Expect poller `backtrace()` / gbt to name a short freelist store
- Soft-skip thr12 / coalesce past zero nodes without recovery-active freelist
  survival + thr11d evidence
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
- Revert SKIP_WILD_W without freeroll proof it breaks a legitimate FB width
- Treat silent thr11d_new=0 as freelist-survival failure (silent never thr11d)

### Reference tags
`[ost-wb] SKIP_WILD_W`, `[ost-wb] SKIP_FL_HDR`, `HIT_SKIP`,
`[fb-fl-writeback]`, `addr=0x1F0D74`, w=1161, `[ssnr-hdr-zero]`,
`[fl-zero-fault] event=fault_ring`, `near_hdr=`, `ring_w=`,
`[adlb-fl-stomp]`, `to_zero_correlate`, `0x801F3CC0`, `0x1F3CC0`,
fail136c, thr11d_new, -391, -407, -408
