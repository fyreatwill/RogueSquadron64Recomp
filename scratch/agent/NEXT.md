# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s645 recap (read this first)

**s644 freeroll consumed — Outcome B (freelist class):**
- freelist to_zero #2 t=164577ms phys=0x1F3CC0 prev_f=0x2 prev_sz=0x60
- thr_with_guest=16 reported=6 — all parked wait/recv (no store leaf)
- H-gbt-writer "names store path at detect" **REFUTED freelist-class**
  (dual-source with menu posctrl)

**Landed BREADCRUMB19** (708 stamps): rs_malloc / rs_free / rs_memset /
heapWalker / buildHeapFreeList. + `[memset-fl-dest]` on rs_memset entry
(first-8 posctrl + freelist-site hits). Gate: `ROGUESQ_LOG_FL_ZERO_WATCH`.

**Same-run / boot posctrl:**
- menu to_zero sticky guest_pc **0x80007904** (rs_memset return-nop) — was
  0x8000834C drainMesh → **BREADCRUMB19 LIVE**
- boot: `[memset-fl-dest] all=0..5 hit=0` within 2s → **probe LIVE**
- sticky-memset ≠ dest proof (menu clear had hit=0)

**Queued:** `scratch/agent/soak_queue/s645_fl_bc19_freeroll.sh`
(SCORE: flz_pc_fl / flz_pc_dms / flz_pc_other / flz_pc_fl_evt / msfl_n)

## This iteration's work unit

**Primary: consume s645 freeroll SOAK-RESULTS (or run if still queued).**

1. Require posctrl: `flz_pc_fl≥1` OR `msfl_n≥1` (menu or freelist) — BC19/probe not cold
2. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60`
3. Discriminators on freelist to_zero #2:
   - **A)** `flz_pc_fl_evt≥1` OR msfl hit covering 0x801F3CC0 near t≈to_zero
     with `ra≠0` → name caller (nm/local-symtab on ra); instrument that leaf
   - **B)** freelist to_zero with flz_pc_dms only / no msfl hit → writer still
     outside freelist+memset class; next: expand breadcrumb to bulk word-store
     idioms that write size/flags without going through rs_* (grep MEM_W(0x0/0x4)
     hot paths in hangar/mission transition), or host-side RDRAM write watch
   - **C)** no freelist to_zero → requeue freeroll once
4. If A fires with a specific ra leaf, next session instruments that leaf only

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
| H-memset-writer | rs_memset zeros freelist header | msfl hit@0x801F3CC0 ∧ freelist to_zero | ACTIVE |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop; dms REFUTED it)
- Treat guest_pc=rs_memset return-nop alone as dest proof without msfl hit=1
- Expect poller `backtrace()` to ever name a guest writer (s643 closed that)
- Expect gbt stacks to catch a short store at 250µs poll (s644/s645 Outcome B)
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
- Re-chase gbt ranking false-positives for host `recomp::` (s644 fixed)

### Reference tags
`[fl-zero-poll]`, `[fl-zero-poll-bt]`, `[fl-zero-poll-gbt]`, `[memset-fl-dest]`,
`[drain-mesh-stomp]`, `[fl-hdr-write]`, `[fl-zero-watch]`, `0x801F3CC0`,
`0x1F3CC0`, BREADCRUMB19, fail136c, thr11d_new, -391, -395, -397, -398, -399
