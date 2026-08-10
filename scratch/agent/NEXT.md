# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s641 recap (read this first)

**Landed (not yet soak-scored):**
- `tools/apply_s641_drain_mesh_stomp.py` → `funcs_3.c` `drainMeshReleaseQueue`
  - 5× `sw $zero,0x4($a0)` → `[drain-mesh-stomp] reg=a0 off=4`
  - 10× `sw $v0,0x0($v1)` when v0==0 → `[drain-mesh-stomp] reg=v1 off=0`
  - TARGET if dest=`0x801F3CC0`; HEAPLIKE if pre_f∈{1,2} and pre_sz sane; else sample
  - Gate: `ROGUESQ_LOG_FL_ZERO_WATCH` (same as fl-zero-poll / fl-hdr-write)
- Binary rebuilt; freeroll queued:
  `scratch/agent/soak_queue/s641_drain_mesh_stomp_freeroll.sh`
  (may already be in `done/` + SOAK-RESULTS if the loop ran it)

**Prior (s640 scored thr11d∧fail136c):**
- H-oob-store CONFIRMED: mid-run `0x2/0x60` → zeros at phys `0x1F3CC0`
- H-walk-into-zeros REFUTED
- guest_pc sticky `0x8000834C` = drainMesh return-nop — not dual-source

## This iteration's work unit

**Primary: consume s641 soak (or re-enqueue if missing) and decide H-drainmesh-stomp.**

1. Read `scratch/agent/SOAK-RESULTS.md` tail + scored log under
   `scratch/agent/soak_results/s641_*`.
2. Require positive controls in the scored run:
   - `[fl-zero-poll] event=heartbeat` (and ideally to_zero)
   - `[drain-mesh-stomp]` sample n≥1 OR document that drainMesh never hit a
     zero-store path (dms_n=0 with heartbeat live → probe gated correctly but
     path cold — not "probe dead")
3. Discriminators on thr11d∧fail136c (or any to_zero):
   - **A)** `[drain-mesh-stomp] ... dest=0x801F3CC0 TARGET` same run as
     `[fl-zero-poll] event=to_zero` → **H-drainmesh-stomp CONFIRMED dual-source**.
     Next: design guard/fix for link-field offset misuse (do not soft-skip
     freelist walk yet).
   - **B)** to_zero fires, dms_tgt=0 (no TARGET) → **drainMesh REFUTED** as
     writer of 0x801F3CC0. Next: widen store search — `rs_memset` / bulk clear
     / other `sw $zero` to sequential heap headers (new apply script).
   - **C)** dms_heap>0 on other addrs without TARGET → class is broader;
     dump dest list; may still need B-style widen for 0x801F3CC0.
4. If soak missing/timeout (rc=137) or recovery_silent only: re-enqueue one
   freeroll clone (do not spend the session babysitting).

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
| H-drainmesh-stomp | drainMesh sw$zero stomps headers | [drain-mesh-stomp]@0x801F3CC0 | ACTIVE (probe LIVE) |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop)
- Soft-skip thr12 / coalesce past zero nodes without writer ID
- Re-open H-zero-free / H-split / H-walk-into-zeros without new counterexample
- Raise HOLD_S past 210
- Spend session on pure thr11d rate soaks
- Merge -385 with -387/-384/-373/-386
- uint32 KSEG0 MEM bases (use S32)
- Use re.sub *string* replacement for C probes containing `\n` in format
  strings (use lambda repl — s641 lesson)

### Reference tags
`[drain-mesh-stomp]`, `[fl-zero-poll]`, `[fl-hdr-write]`, `[fl-zero-watch]`,
`0x801F3CC0`, `0x1F3CC0`, `drainMeshReleaseQueue`, `0x8000834C`, fail136c,
thr11d_new, -391, -395, -385, apply_s641
