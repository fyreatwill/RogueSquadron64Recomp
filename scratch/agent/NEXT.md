# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s644 recap (read this first)

**Landed `[fl-zero-poll-gbt]`** in `src/main/main.cpp` `start_fl_zero_poller`
on `event=to_zero`: `task_threads` → suspend → ARM64 FP walk (safe
`mach_vm_read_overwrite`) → guest-ranked dump (cap 6 thr × 32 frames).

**Same-run posctrl** (driven HOLD_S=70, tag
`s644_flz_gbt_posctrl_v2_20260810140015`):
- menu to_zero #1 t_ms=51542 prev_f=0x8E8E prev_sz=0x8E8E8E8E → zeros
- summary: `thr_with_guest=17 reported=6 nsnap=19`
- top: `menuOverlayInit` / `mainEventQueueWorker` / `saveServiceWorker` /
  `startServiceWorker` — all in `wait_for_resumed`/`osRecvMesg`
- **Posctrl CONFIRMED**: sampler reaches real OSThread hosts
- **Writer not on stack** at menu to_zero (short clear already returned)

**s643 freeroll folded:** Outcome C (no freelist-shaped to_zero; recovery
silent). Prior s642 freelist 2/2 still dual-source.

**Queued:** `scratch/agent/soak_queue/s644_flz_gbt_freeroll.sh`
(SCORE includes `flz_gbt=` / `flz_gbt_guest=` / `flz_gbt_frames=`; dumps gbt).

## This iteration's work unit

**Primary: consume s644 freeroll SOAK-RESULTS (or run if still queued).**

1. Require posctrl: `flz_gbt_guest≥1` (menu or freelist) — instrument not cold
2. Freelist-shaped: `to_zero` with `prev_f=0x2 prev_sz=0x60` (or thr11d∧fail136c)
3. Discriminators on freelist to_zero #2:
   - **A)** any reported thr has guest leaf `rs_malloc` / `rs_memset` /
     `rs_free` / `heapFree*` / bulk clear mid-body → instrument that class
     (fixup probe on the named store sites)
   - **B)** all game thr parked wait/recv (same as menu posctrl) → expand
     `g_rs64_last_guest_pc` audited set on freelist header store idioms
     (grep `MEM_W`/`MEM_H` near heap freelist helpers; batch into fixup)
   - **C)** no freelist to_zero → requeue freeroll once; do not expand
     last-guest-pc until freelist-shaped event is in hand
4. If A fires with a specific leaf, next session instruments that leaf only
   (not a whole-idiom expansion until 2nd independent hit).

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
| H-gbt-writer | game-thread BT names store path | [fl-zero-poll-gbt] guest leaf on freelist to_zero | ACTIVE (posctrl LIVE; freelist pending) |
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
- Re-chase gbt ranking false-positives for host `recomp::` (s644 fixed)

### Reference tags
`[fl-zero-poll]`, `[fl-zero-poll-bt]`, `[fl-zero-poll-gbt]`, `[drain-mesh-stomp]`,
`[fl-hdr-write]`, `[fl-zero-watch]`, `0x801F3CC0`, `0x1F3CC0`, fail136c,
thr11d_new, -391, -395, -397, -398, start_fl_zero_poller, fl_zero_sample_game_threads
