# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s640 recap (read this first)

**s639 soak consumed (scored thr11d∧fail136c):**
- Positive controls LIVE: fl-zero-poll heartbeats, fl-hdr-write flags=1, fl-zero-watch control
- **H-oob-store CONFIRMED** — mid-run phys `0x1F3CC0` held allocated header
  `flags=0x2 size=0x60` for ~20s then full zeros (to_zero #2 t≈165s)
- **H-walk-into-zeros REFUTED** — first zero_node prev=`0x801ED1B0` prev_sz=`0x6B00`
  correctly yields next=`0x801F3CC0` (prev+0x10+sz)
- zero_node first at **site=malloc** immediately after to_zero #2 (not only at fail136c)
- fail136c still i=54 free `0x20`@`0x801F3C90` → i=55 zeros@`0x801F3CC0`
- thr11d rate **4/10**
- **Writer ID NOT dual-source:** `guest_pc=0x8000834C` is
  `drainMeshReleaseQueue` return-nop — known sticky last-guest-pc trap
  (PROJECT-OVERVIEW §10). Static: drainMesh `sw $zero,0(v1)` + `sw $zero,4(a0)`
  *can* stomp flags/size if a0/v1 is a sequential heap header — unproven live.

## This iteration's work unit

**Primary: dual-source the zeroing STORE (item -395).**

1. Add fixup-gated probe in `drainMeshReleaseQueue` (funcs_3.c via
   `tools/fixup_game_funcs.py` or a small `tools/apply_s640_drain_mesh_stomp.py`
   called from fixup) on every `MEM_W(...)=0` / `sw $zero` site that writes
   through a0 or v1:
   - Before write, read pre flags=HU(+0), size=W(+4)
   - Log `[drain-mesh-stomp]` when:
     - dest == `0x801F3CC0`, OR
     - pre flags∈{1,2} and pre size≠0 and size looks heap-sane (<0x800000)
   - Fields: site_pc, dest, pre_f, pre_sz, which_reg (a0|v1), ra
   - Gate: `ROGUESQ_LOG_FL_ZERO_WATCH` (same as existing FL instruments)
2. Optional same build: log malloc path that writes flags=0x2 at a header
   (creation of `0x2/0x60` at 0x801F3CC0 was not in fl-hdr-write free/split).
3. Rebuild RecompiledFuncs + game (no full regen unless fixup-only apply).
4. Enqueue freeroll recipe (clone s639) with FL_ZERO_WATCH=1; do NOT babysit.
5. Discriminators on thr11d∧fail136c (or any to_zero #2):
   - **A)** `[drain-mesh-stomp] dest=0x801F3CC0` same run as to_zero → drainMesh
     CONFIRMED dual-source → design guard/fix for link-field offset misuse
   - **B)** to_zero fires, drain-mesh-stomp never on that addr → drainMesh
     REFUTED as writer; widen store search (rs_memset, other sw $zero idioms)
   - **C)** stomp fires on other headers with flags=2 → class is broader
     freelist-link-vs-sequential-header collision

Positive control same run: existing fl-zero-poll heartbeat + at least one
`[drain-mesh-stomp]` OR a deliberate note that drainMesh ran (counter of
zero-stores sampled) so silence is not "probe dead".

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
| H-drainmesh-stomp | drainMesh sw$zero stomps headers | [drain-mesh-stomp]@0x801F3CC0 | ACTIVE |
| H-shipn3-gate / Outcome A | B8→store→thr11d | live chain | CONFIRMED s637/s638 |

## Do NOT
- Treat guest_pc=0x8000834C alone as writer proof (sticky nop)
- Soft-skip thr12 / coalesce past zero nodes without writer ID
- Re-open H-zero-free / H-split / H-walk-into-zeros without new counterexample
- Raise HOLD_S past 210
- Spend session on pure thr11d rate soaks
- Merge -385 with -387/-384/-373/-386
- uint32 KSEG0 MEM bases (use S32)

### Reference tags
`[drain-mesh-stomp]`, `[fl-zero-poll]`, `[fl-hdr-write]`, `[fl-zero-watch]`,
`0x801F3CC0`, `0x1F3CC0`, `drainMeshReleaseQueue`, `0x8000834C`, fail136c,
thr11d_new, -391, -395, -385
