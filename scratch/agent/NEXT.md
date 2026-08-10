# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s639 recap (read this first)

**Static freelist writer audit CLOSED for two hypotheses:**
- H-zero-free REFUTED — `rs_free` only sets flags=1; never zeros size
- H-split-bug REFUTED — residual only when rem≥0x20; residual size ≥ 0x10
- Live posctrl (25s boot): 70× `[fl-hdr-write]` free/split all flags=1 size>0;
  `[fl-zero-watch] event=control` maxfree sane; `[fl-zero-poll]` armed on
  phys 0x1F3CC0 (starts zero before freelist grows there)

**Still open:** who creates mid-run E8 node at `0x801F3CC0 flags=0 size=0`
(s638 FED). Residual: H-oob-store or walk-into-zeros (prev size too small).

**Enqueued:** `s639_fl_zero_writer_freeroll.sh` — thr11d freeroll with
`ROGUESQ_LOG_FL_ZERO_WATCH=1` + all passive breadcrumbs.

## This iteration's work unit

**Primary: consume s639 soak (or re-run if queue empty) and classify writer.**

1. **Consume SOAK-RESULTS** for s639_fl_zero_writer_freeroll:
   - Positive control must fire in scored log: heartbeat, fl-hdr-write free
     flags=1, fl-zero-watch control. If missing → instrument not armed.
   - On thr11d_new∧fail136c: classify A–E from recipe header.
   - Key greps:
     ```
     grep -E 'fl-zero-poll.*(to_zero|heartbeat|arm)|fl-hdr-write|fl-zero-watch|fail136c|thr11d' LOG
     ```

2. **If to_zero fires with guest_pc:** map PC (nm local-symtab); if outside
   allocator → H-oob-store CONFIRMED single-source; need 2nd hit for dual.
   If inside free/malloc/coalesce despite static → re-read that site live.

3. **If zero_node site=free|malloc first:** attribute last allocator exit;
   dump prev node (prev_f/prev_sz) — if prev is free size=0x20 at 0x801F3C90
   matching s638, check whether size was truncated earlier via fl-hdr-write.

4. **If only fail136c sees zero_node (E):** corruption between last free/malloc
   exit and loadLevelTextureCache — arm denser poll or watch more addrs.

5. **If soak recovery_silent only (null again):** do NOT spend another full
   session babysitting rate. Either leave another freeroll queued OR pivot to
   offline: search guest code that MEMSET/bzero regions near freelist after
   thr11d (ship destroy / sec4 path).

## Hypotheses

| ID | Claim | Discriminator | Status |
|----|-------|---------------|--------|
| H-ltexmg1 | guard LIVE | ltexmg≥1 ∧ ltex_null=0 | CONFIRMED |
| H-walk1 | S32 MEM_* | posctrl sane | CONFIRMED s626 |
| H-E8-corrupt | zero-node mid E8 | raw @0x801F3CC0 | CONFIRMED s638 |
| H-zero-free | free zeros header | fl-hdr-write size=0 | **REFUTED s639** |
| H-split-bug | split size=0 residual | fl-hdr-write split size=0 | **REFUTED s639** |
| H-oob-store | external stomp | fl-zero-poll to_zero guest_pc ∉ allocator | ACTIVE |
| H-walk-into-zeros | prev size wrong → land on zeros | prev_sz too small vs real free span | ACTIVE |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |
| H-b8rate residual | no-destroy = no thr | freeroll | pending |

## Do NOT
- Soft-skip thr12 / coalesce past zero nodes without writer ID
- Re-open H-zero-free / H-split without new counterexample
- Raise HOLD_S past 210
- Spend session on pure thr11d rate soaks without FL_ZERO data
- Merge -385 with -387/-384/-373/-386
- uint32 KSEG0 MEM bases (use S32)

### Reference tags
`[fl-zero-poll]`, `[fl-hdr-write]`, `[fl-zero-watch]`, `0x801F3CC0`, `0x1F3CC0`,
`ROGUESQ_LOG_FL_ZERO_WATCH`, fail136c, thr11d_new, -391, -394, -385
