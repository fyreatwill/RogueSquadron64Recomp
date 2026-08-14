# NEXT work unit (s1108)

HYPOTHESIS-ID: submit-producer-boundary

s1107 (checkpoint iteration, no build/run) narrowed but did not change the
plan: `0x8011A89C..0x8011A8A0` sits in the SP/DP scheduler's own unlabeled
static block (no symbol between `D_8011A7E8` and `D_8011A8D0` in
`syms/rogue_squadron.datasyms.toml`) and does not overlap any known overlay
DMA destination, so a DMA/preexisting-ROM-content explanation is ruled out —
`H-nongenerated-writer` now means an actual non-generated code path, not a
load-time artifact.

Add regeneration-safe generated-store probes for every `MEM_B`, `MEM_H`, and
`MEM_W` whose resolved physical target can be `0x11A89F` or `0x11A8A0`.
Record phase, store PC, width, address, value, and the next submit-boundary
row; do not change queue behavior. Apply the probe through the normal fixup
path, build, and run the same VI-1024-gated capture with the positive VI/E9
controls and `ROGUESQ_LOG_SUBMIT_BOUNDARY=1`.

Implementation note (not yet verified against the current tree): `MEM_B`/
`MEM_H`/`MEM_W` are defined once, as macros, in
`lib/N64ModernRuntime/N64Recomp/include/recomp.h` (an lvalue-returning
dereference expression used both for loads and for `MEM_X(...) = value;`
stores). Redefining that macro globally to add a runtime address check on
every single memory access in the game is a large, hot-path, whole-codebase
risk for a two-address investigation — avoid it. Prefer a bounded fixup pass
that greps generated `funcs_*.c` (regenerated from the `N64Recomp` working
tree, not present in this repo — see `fixup_game_funcs.py` there) for the
literal assignment pattern `MEM_[BHW](...) = ...;`, and inserts a guarded
check only where the offset/register pair cannot be statically excluded from
resolving near `0x8011A89C`. Confirm this file layout is still current before
building on it; do not assume it unchanged from this note.

Competing hypotheses:

* H-generated-writer: a generated store writes the nonzero `0x8011A8A0` value.
* H-nongenerated-writer: no generated store fires before the nonzero submit
  row, so ownership is an actual non-generated code path (not, per s1107, a
  DMA/preexisting-content artifact).
* H-observation-race: the store probe and submit rows do not establish order
  because the shared guest-PC/value observation is cross-thread or the phase
  scope is wrong.

Discriminator: a writer row for `0x11A8A0` preceding a same-phase SP send
selects H-generated-writer; positive controls plus repeated nonzero submit
values and zero generated-writer rows select H-nongenerated-writer; missing
phase/order controls make the capture invalid and require fixing the probe.

Exact baseline command:

```sh
env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_LOG_SUBMIT_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/submit_boundary_writer 60 1.0
```

This is a large work unit (touches the regeneration pipeline across many
generated files or a shared macro). Budget it as its own iteration; do not
start it inside another checkpoint/closeout pass.
