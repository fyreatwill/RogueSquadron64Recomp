# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s643 recap (read this first)

**Landed `[fl-zero-poll-bt]`** in `src/main/main.cpp` `start_fl_zero_poller` on
`event=to_zero` (≤32 frames, rate-limit 16, `dladdr` + `backtrace_symbols`).

**Same-run posctrl** (driven HOLD_S=70, tag
`s643_flz_bt_posctrl_drv_20260810133121`):
- menu to_zero #1 t_ms=51745 prev_f=0x8E8E prev_sz=0x8E8E8E8E → zeros
- `[fl-zero-poll-bt] n=8 to_zero_n=1 frames=6 guest_pc=0x8000834C`
- frames: `start_fl_zero_poller` lambda → pthread only — **no recomp leaf**
- **Outcome B structural**: poller is a side thread; host BT cannot name the
  guest writer. H-hostbt-writer "poller BT names store path" **REFUTED** for
  naming (instrument still useful as posctrl tag).

**Queued:** `scratch/agent/soak_queue/s643_flz_bt_freeroll.sh`
(SCORE includes `flz_bt=` / `flz_bt_frames=`; dumps BT block).

## This iteration's work unit

**Primary: consume s643 freeroll SOAK-RESULTS (or run if still queued), then
land the next attribution path for freelist-shaped to_zero.**

1. Read new SOAK-RESULTS line(s) for `s643_flz_bt_freeroll`. Require:
   - posctrl: `flz_bt≥1` (menu to_zero or freelist) — instrument not cold
   - freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60` (or thr11d∧fail136c)
2. If freelist to_zero fires with poller-only BT (expected B): **do not**
   re-chase poller BT. Pivot this same session to ONE of:
   - **(preferred)** Sample the **game recomp thread** stack at to_zero detect
     (pthread list / known game-thread handle; not the poller thread). Cap
     frames ≤32, tag `[fl-zero-poll-gbt]`, same-run posctrl = menu to_zero #1
     must show recomp/`rs_malloc`/memset-class frames if the writer is on that
     thread; pure runtime still = uninstrumented path.
   - **OR** expand `g_rs64_last_guest_pc` audited set on freelist header store
     idioms (grep `MEM_W`/`MEM_H` near heap freelist helpers; batch into fixup).
3. If freelist to_zero never fires (C): requeue freeroll once; do not expand
   BT tooling until freelist-shaped event is in hand.
4. Discriminators for game-thread BT (if built):
   - **Posctrl:** menu to_zero #1 prints ≥1 `[fl-zero-poll-gbt]` with a non-
     poller frame.
   - **A)** freelist to_zero #2 frames name recomp helper / bulk clear →
     instrument that class.
   - **B)** only runtime/ultramodern/recomp trampoline with sticky guest_pc →
     expand audited last-guest-pc on freelist store sites.
   - **C)** no freelist to_zero this soak → freeroll only.

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
| H-hostbt-writer | poller BT names real store path | [fl-zero-poll-bt] recomp leaf | **REFUTED s643** (B structural) |
| H-gbt-writer | game-thread BT names store path | [fl-zero-poll-gbt] on freelist to_zero | ACTIVE next |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop; dms REFUTED it)
- Expect poller `backtrace()` to ever name a guest writer (s643 closed that)
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
`[fl-zero-poll]`, `[fl-zero-poll-bt]`, `[fl-zero-poll-gbt]`, `[drain-mesh-stomp]`,
`[fl-hdr-write]`, `[fl-zero-watch]`, `0x801F3CC0`, `0x1F3CC0`, fail136c,
thr11d_new, -391, -395, -396, -397, start_fl_zero_poller
