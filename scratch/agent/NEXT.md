# NEXT: G1c dd4 frame cost - where does the extra send_dl time go?
HYPOTHESIS-ID: g1c-dd4-gfx-task-cost

s6697: fixed build, lvl5 dd1 30.0 fps / 14.7 ms per gfx task, dd4 19.6 fps / 33.9 ms (cpu-bound, cpu 32.9). lvl1 dd4 24.1 / 24 ms.
G3d closed on data (no residual jerk retail or FPS60); owner judges feel.

Hypotheses for the dd4 per-task cost: H-verts (cost scales with vertices transformed/clipped - more terrain cells),
H-tris (scales with RDP triangle emission / RT64 command intake), H-ucap (the ucode iteration cap lets long DL loops run),
H-overhead (fixed per-op host overhead in our LLE RSP, e.g. remaining diagnostic hooks like s6372's, that dd4 multiplies).
Discriminator, ONE build: per gfx task log vertex count, triangle count, RSP instructions/vector ops executed and send_dl
wall; macOS `sample` of the Gfx thread for 10 s in lvl5 dd4 flight (no build needed, do this FIRST - it names hot functions
directly). If a diagnostic hook or getenv shows in the profile -> H-overhead, remove it. If ms/task is linear in verts with
the same slope at dd1 and dd4 -> H-verts (optimise the vertex path or accept). Recipe:
env ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA="ROGUESQ_DRAW_DISTANCE=4 " HOLD_S=180 LEVEL=5 TAG_SUFFIX=sNNNN_dd4 zsh scratch/agent/g1_level_coverage_common.zsh
Owner: judge turning feel (retail and FPS60) on the fixed build; send s6694/s6695 21:9 level-select frames.
