# NEXT: identify a host RDRAM writer at the phase-5→phase-6 red boundary
HYPOTHESIS-ID: g3c-owner-visual

s6348 passed the ordinary-store, VTX, bulk, and forced-red controls and
captured 44 phase-5 target-store/post pairs. The only target writers were
pointer/list-shaped `0x8000D114` stores plus one zero store at `0x80010FCC`;
none produced the independent red VTX-boundary word. Five phase-6 boundary
reads stayed red and had zero phase-5 DMA overlap.

Competing hypotheses:

- H-host-target-write: a host RDRAM API writes `0x735560..0x7355D0` after the
  guest-store census and creates the red bytes.
- H-earlier-copy: the red bytes are created by an earlier or uninstrumented
  copy before the current host-write hooks observe the range.
- H-order-gap: the phase labels or source-boundary sampling leave an ordering
  gap, so a writer is attributed to the wrong phase.

Discriminator: add one target-range host-write census to the existing shadow
for every host write API, retaining API/sequence/phase, target overlap,
pre-bytes, payload or source bytes, and post-bytes. A first post-write red
transition selects H-host-target-write and names the API; no target host write
with all ordinary-store, VTX, bulk, and forced-red controls firing selects
H-earlier-copy; inconsistent phase/sequence ordering selects H-order-gap.

Bounded work unit: add the host target-range census to the existing
`rs64_f5_host_write_begin`/`rs64_f5_host_write_after` and bulk paths, build once,
then run one DD3 level-1 arm:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6349_host_target_write' zsh scratch/agent/g1_level_coverage_common.zsh`

Judge `keys.log`, all positive controls, target host-write rows, and the
phase-6 `0x735560..0x7355D0` boundary bytes. Do not add fade/cull mitigation.
