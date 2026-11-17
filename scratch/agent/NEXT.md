# NEXT (s7502)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7501_ez_levels (tools/s7501_ez_recipe.zsh; `s7501_ez_levels ez arm=` rows in scratch/s7501_ez_levels/out.txt).
score 0 / 5 with ctlst=ok on L1 dd8 21:9, L7, L10, L12 dd4 and no new writer function -> EZ CLOSED 6 levels. ctlst!=ok -> instrument fault.
A cpu writer fn outside {rs_memset, parseImageFile, hud*, buildHeapFreeList, rs_free, rs_malloc*, coalesceFreeHeapBlocks*} is the work unit.

Work unit, class FA: s7501 found 4-5 uploads per arm whose writer is the heap allocator (buildHeapFreeList / rs_free / rs_malloc /
coalesce) writing block headers into RAM of a framebuffer RT64 still tracks. Hypotheses: H-fa-dead (the image is never set again, or is
set and filled before any draw/present/texture read: harmless stale tracking) / H-fa-live (the image is live: set this or next swap, or
presented by VI, and RT64 shows or samples the uploaded heap bytes: visible garbage) / H-fa-retail (retail frees and reuses the same RAM
the same way; the upload is only an RT64 tracking cost).
Discriminator, ONE build: in rs64_s7501_up, when cls=cpu and fn is an allocator, register the fb with the s7500 EY tracker (rs64_s7500_*
already classifies the first later event on an image: fill / draw / zread / tex / up / wb) and also log whether VI origin == that fb
within the next 3 swaps (rs64 VI origin hook). Control: the s7501 ctl word on a live fb must classify as live (draw/present).
Run: `env XC=ROGUESQ_S7500_EY=1+ROGUESQ_S7500_CTL=1 zsh tools/s7501_ez_recipe.zsh` (L4 dd1, L15 dd8 21:9).
Outcome: all allocator uploads -> dead/fill-first => H-fa-dead, class closed; any draw/present/tex before fill => H-fa-live, then name
why RT64 keeps a freed fb live and check retail via the oracle (mupen watch on that block).
