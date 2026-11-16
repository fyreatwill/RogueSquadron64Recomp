# NEXT (s7490)
HYPOTHESIS-ID: m3-store-path-coverage

s7489 closed EN: guest store census exit 0 (tools/s7489_store_path_census.py), host DMA writes (sp_wr_gfx/sp_wr_aud/pi_dma) host_wF=0
on L4/L15 with the write plant DETECTED in flight. Levels soak s7489_hostwrite_levels (L1 dd8 21:9, L7/L10/L12) is queued: fold it first
(score=0 -> EN host-DMA side closed for 6 levels; any host_wF/host_wUrec -> chase the `[s7486] host-uaf kind=sp_wr_*|pi_dma loc=F|R` row).

Work unit (class EO, last of the store side): host writes through guest pointers that are NOT DMA.
1. Offline census (no run): grep lib/N64ModernRuntime/{librecomp,ultramodern}/src and src/ for host stores into RDRAM via guest pointers
   (MEM_W/MEM_H/MEM_B assignments, TO_PTR(...)-> field writes, memcpy into rdram + addr): osRecvMesg / osSendMesg message slots,
   pi.cpp:722 IoMesg fields, osContGetReadData pad structs, EEPROM/save reads, RT64 framebuffer readback to RDRAM. Tool:
   tools/s7490_hostwrite_census.py -> table (site, writer, dest pointer source, bytes).
2. Route each live site through rs64_s7486_hostread with a new kind (9 mesg, 10 iomesg, 11 cont, 12 fb_rb...; arrays already sized for 9 ->
   widen to 16), one build; rerun tools/s7489_hostwrite_recipe.zsh LV="4:4 15:8" HOLD=220 with a mesg-specific plant if sp_wr_gfx stays the only
   plant kind.
Hypotheses: H-eo-clean (no host write lands in a still-free block) / H-mesg-uaf (a freed OSMesgQueue/msg buffer is written by the host
scheduler) / H-eo-none (no non-DMA host write targets heap at all: then say so from the census and close).
If EO closes clean, the M3 heap-audit series is DONE: take CURRENT-TRUTH item 20 / ITERATION 3c next rung.
