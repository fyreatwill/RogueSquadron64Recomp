# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s642 recap (read this first)

**Offline-scored s641 soak (outer rc=137, att1 run.log ~560s):**
- Posctrl LIVE: `[fl-zero-poll]` heartbeats + `[drain-mesh-stomp]` n=34 all `sample`
- dms dest exclusive **0x807xxxxx** mesh pool; dms_tgt=0 dms_heap=0; only reg=a0 off=4
- to_zero #1 t_ms=51254: texture `0x8E8E…` → zeros at phys `0x1F3CC0`, sticky
  guest_pc=`0x8000834C`, **no TARGET**
- **H-drainmesh-stomp REFUTED** dual-source (probe fires elsewhere; to_zero w/o TARGET)
- No freelist-shaped to_zero #2 (force6=0 hsel=0 craft-select hold)
- Freeroll retry queued: `scratch/agent/soak_queue/s642_drain_mesh_stomp_freeroll_retry.sh`

**Still open:** freelist-shaped writer of `0x2/0x60`→0 at `0x801F3CC0` (H-oob-store event).

## This iteration's work unit

**Primary: land host backtrace on `[fl-zero-poll] event=to_zero` (-396).**

1. Edit `src/main/main.cpp` `start_fl_zero_poller` — on `kind=="to_zero"`, dump
   host stack via existing `backtrace`/`backtrace_symbols` pattern already used
   elsewhere in main.cpp (macOS; `ROGUESQ_HWBP` is Win32-only / unsupported here).
2. Tag e.g. `[fl-zero-poll-bt]` frames under the to_zero line. Cap frames (≤32)
   and rate-limit if needed (menu to_zero #1 + freelist #2 are rare).
3. Rebuild binary only (`cmake --build build -j8 --target RogueSquadron64Recomp`).
   No regen. No lib/ edit → no export.sh.
4. Enqueue freeroll with `ROGUESQ_LOG_FL_ZERO_WATCH=1` (clone s642 retry recipe;
   SCORE can count `flz_bt=` lines). Keep dms arm passive.
5. Discriminators (same-run):
   - **Posctrl:** menu to_zero #1 (~51s) prints ≥1 `[fl-zero-poll-bt]` frame line.
     No frames on to_zero → probe dead; fix before interpreting freelist hit.
   - **A)** freelist-shaped to_zero #2 (`prev_f=0x2 prev_sz=0x60`) host frames
     name a recomp helper / bulk clear / known store site → instrument that class.
   - **B)** frames only in poller/runtime with no recomp leaf → writer is
     uninstrumented guest path; use top non-runtime frame + `g_rs64_last_guest_pc`
     together; consider expanding audited last-guest-pc set.
   - **C)** to_zero #2 never fires this soak → consume freeroll retry only;
     do not declare writer.

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
| H-hostbt-writer | host BT names real store path | [fl-zero-poll-bt] on freelist to_zero | ACTIVE |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop; dms REFUTED it)
- Soft-skip thr12 / coalesce past zero nodes without writer ID
- Re-open H-drainmesh-stomp / H-zero-free / H-split / H-walk-into-zeros without
  new counterexample (dms TARGET@0x801F3CC0 on freelist to_zero would reopen)
- Raise HOLD_S past 210
- Spend session on pure thr11d rate soaks
- Merge -385 with -387/-384/-373/-386
- uint32 KSEG0 MEM bases (use S32)
- Use re.sub *string* replacement for C probes containing `\n` in format
  strings (use lambda repl — s641 lesson)
- Try ROGUESQ_HWBP on macOS (prints "not supported")

### Reference tags
`[fl-zero-poll]`, `[fl-zero-poll-bt]`, `[drain-mesh-stomp]`, `[fl-hdr-write]`,
`[fl-zero-watch]`, `0x801F3CC0`, `0x1F3CC0`, fail136c, thr11d_new, -391, -395,
-396, apply_s641, start_fl_zero_poller
