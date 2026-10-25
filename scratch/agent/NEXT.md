# NEXT: G1d isolate the menu/hangar buffer contract after width rewrite
HYPOTHESIS-ID: g1d-widescreen

s6167 confirmed the game-side writer: with the opt-in 512x340 rewrite, wide
phase 5 emits `ci_w=796`, scissor `3184x1360`, and VI width 796; control stays
at 512. The wide arm then crashed 5/5 in `renderLitTexturedMeshFaces+7948`
before mission, so no post-change framebuffer dump was valid.

Work unit: trace the menu/hangar framebuffer allocation and consumer contract
for one 16:9/12 MB arm, using the existing route probe plus framebuffer
address/stride diagnostics. Do not widen another writer or add a guard.

Competing hypotheses and discriminator:
- H-menu-fb-allocation: the menu/hangar flip or intermediate buffers remain
  512-stride/size while CI/scissor are 796; allocation/base/stride rows will
  disagree with the phase-5 CI and explain the renderer crash.
- H-menu-render-input: buffer geometry agrees, but the widened scissor exposes
  an invalid menu display-list coordinate/texture path; the crash remains with
  matching allocation rows and the renderer's first bad input identifies it.
- H-wide-RT64: guest buffer geometry and RDP inputs agree, but RT64's menu
  readback/present path rejects the widened target; guest rows are consistent
  while the first RT64 consumer reports the mismatch.

Discriminator: in one build/run, positive-control the existing 4:3 menu route
and the 16:9/12 MB route; capture the first menu/hangar framebuffer alloc,
colour-image, scissor, VI origin/width, and renderer crash/input rows. An
allocation/stride mismatch selects H-menu-fb-allocation; consistent guest
geometry with a bad draw selects H-menu-render-input; consistent guest and RDP
geometry with an RT64-side failure selects H-wide-RT64. Keep default retail
unchanged and preserve the current s6167 writer hook until this is resolved.
