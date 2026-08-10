# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s646 recap (read this first)

**s645 freeroll consumed — Outcome B (freelist + memset class):**
- att2 freelist to_zero #2 t=164762 phys=0x1F3CC0 prev_f=0x2 prev_sz=0x60
- sticky guest_pc=0x8000834C drainMesh (NOT freelist-class despite BC19)
- msfl hit=0 (76 probes) → **H-memset-writer REFUTED freelist-class**
- gbt thr_with_guest=16 reported=6 all parked (Outcome B reconfirm)
- placement 0x2/0x60 @ t=145420 sticky 0x80007904 (sticky ≠ dest proof)

**Landed `[fl-zero-fault]` mprotect watch** (gate ROGUESQ_LOG_FL_ZERO_WATCH):
- arm PROT_READ while header zeros (boot) or freelist 0x2/0x60
- SIGSEGV → host PC local-symtab + guest sticky; re-enable RW; poller re-arms
- **Posctrl LIVE:** fault_n=17, first leaf rs_malloc+0x12a0; CRASH=0

**Queued:** `scratch/agent/soak_queue/s646_fl_fault_freeroll.sh`
(SCORE: flz_fault_n / flz_fault_hdr / flz_fault_arm_fl / flz_fault_sym)

## This iteration's work unit

**Primary: consume s646 freeroll SOAK-RESULTS (or run if still queued).**

1. Posctrl: `flz_fault_n≥1` (boot-zero arm must fire) — instrument not cold
2. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60`
3. Require `flz_fault_arm_fl≥1` (armed for freelist window)
4. Discriminators on freelist window / to_zero:
   - **A)** `flz_fault_hdr≥1` near freelist to_zero with `flz_fault_sym` naming
     a recomp leaf (or host `recomp::` / bulk path) → instrument that leaf only
     for zero-store of flags/size; next session hardens a targeted guard or
     breadcrumb at that site
   - **B)** arm_freelist≥1 but flz_fault_hdr=0 (only in_hdr=0 neighbor thrash)
     → tighten arm (byte-range re-check after fault; or arm later / single-shot
     after 0x2/0x60 stable ≥1s); do not expand breadcrumb scattershot
   - **C)** no freelist to_zero → requeue freeroll once
5. If A fires with a specific leaf, next session instruments that leaf only

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
| H-fault-writer | mprotect names freelist stomp leaf | flz_fault_hdr≥1 ∧ flz_fault_sym | ACTIVE |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
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
- Try ROGUESQ_HWBP on macOS (prints "not supported") — use fl-zero-fault instead
- Re-chase gbt ranking false-positives for host `recomp::` (s644 fixed)
- Expand freelist breadcrumb scattershot before consuming fault freeroll (A/B)

### Reference tags
`[fl-zero-fault]`, `[fl-zero-poll]`, `[fl-zero-poll-bt]`, `[fl-zero-poll-gbt]`,
`[memset-fl-dest]`, `[drain-mesh-stomp]`, `[fl-hdr-write]`, `[fl-zero-watch]`,
`0x801F3CC0`, `0x1F3CC0`, BREADCRUMB19, fail136c, thr11d_new, -391, -395,
-397, -398, -399, -400
