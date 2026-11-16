# NEXT (s7486)
HYPOTHESIS-ID: m3-host-uaf-reads

s7485 closed EI (guest loads of freed blocks, 6 levels, plant DETECTED every arm) and EJ (retail-benign over-reads,
tools/s7485_overread_bound.py). The remaining uncovered reader of freed heap is the HOST side (class EK).

Work unit: one instrument, one build. Under ROGUESQ_S7486_HOSTUAF=1 (+ S7480_UAF + S7475_CANARY), hook every host read of guest
RDRAM that can follow a guest pointer: RSP SP DMA RDRAM->DMEM (lib/N64ModernRuntime/librecomp/src/rsp.cpp + src/rsp/s7094_dma_shape.cpp
for the shape), RDP command/texture fetch addresses as dpc_bridge.cpp hands them to RT64 (LoadBlock/LoadTile/SetTextureImage +
DL segment reads), AI DMA source. For each range call a new rs64_s7486_hostread(kind, addr, len) beside rs64_s7484_load in
src/main/upstream_compat.cpp: bitmap test, locator class F/Urec/U/N/S (same as EH/EI), per-kind first-hit log + summary.
Controls (same run): ctl = count of DMA ranges inside LIVE canary blocks (must be >0, proves the bitmap path sees host reads);
plant = mark the block holding the current gfx task's DL as freed for one frame (ROGUESQ_S7486_PLANT=<s>) -> must be DETECTED kind=sp_dma.
Recipe: copy tools/s7484_uafload_recipe.zsh -> tools/s7486_hostuaf_recipe.zsh, LV="4:4 15:8" HOLD=220 in-session, then queue L1/L7/L10/L12.
If lib/ is edited: ./submodule-patches/export.sh + commit.
Hypotheses: H-host-clean (0 F/Urec host reads) / H-host-uaf (F rows name the DMA kind and the freeing caller; G5b terrain-drop lead if
kind=rdp_tex or sp_dma on dd>1) / H-host-stale-DL (a DL references a block freed earlier the same frame: S/Urec rows at task time).
Discriminator: locator class at DMA time, per kind, with the plant DETECTED.
