# NEXT work unit (within-run A/B of the Factor 5 triangle map)

HYPOTHESIS-ID: m3-drawindexed-copy-cycle

Build both the current consume-only Factor 5 `0xB4/0xBF` map and a
reference-shaped handler arm in one iteration, then run a phase-gated within-
run A/B. Batch positive E9 provenance, VI width, triangle dispatch, copy-cycle,
and DL-sync controls in the same build and capture. Do not add a mitigation or
classify operand legitimacy.

Competing hypotheses and discriminator:

- H-map-load-bearing: the reference-shaped arm increases legitimate triangle
  dispatch/emission and changes copy-cycle or DL-sync outcomes.
- H-map-intentional: the reference-shaped arm does not improve controls or
  introduces stream drift, so another producer/path is required.
- H-map-garbage: candidates are not valid triangles, so decoding them produces
  no legitimate geometry and the map discrepancy is incidental.

Discriminator: compare per-arm triangle handler/emission counts, copy-cycle
assertions, and DL-sync progression within the same phase/VI population. A
positive-control-preserving geometry increase with improved sync selects
H-map-load-bearing; unchanged or worsened behavior with opcode/operand drift
selects H-map-intentional or H-map-garbage. Any mitigation still requires an
ORIGIN naming the writer and a legitimacy assessment.

Exact execution: add both map arms and one in-process toggle, then run
`cmake --build build --config Debug --target RogueSquadron64Recomp`; execute
`env ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_DISPATCH=1
ROGUESQ_LOG_RDP_ADVANCE=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_DL_SYNC=1
ROGUESQ_LOG_TRI_COPY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1
zsh scratch/agent/s790_postsec2_reachability.sh` from the repo root, with the
script's `build/` launch and watchdog retained. Use SIGKILL for timeout. Do
not run a cross-run animating-scene comparison.

Evidence from s844/s845: the phase-gated run reached VI 1024 and produced 392
positive E9 provenance rows. It recorded 112 candidate rows (37 B4, 75 BF;
54 textured), zero draw rows, and zero copy-assert rows. The reference maps
both opcodes to geometry with conditional 8/24-byte totals, while RT64 maps
both to unconditional consume16. The run later hit slotDispatcherIter+872 at
202.8s. No writer/legitimacy claim exists.

Exact execution: use `rg` and bounded `sed` windows to enumerate every
0xB4/0xBF map, handler, fixup, and generated-source definition; compare the
call graph and command-length behavior with `docs/F5-UCODE-REFERENCE.md`.
