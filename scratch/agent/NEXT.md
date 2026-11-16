# NEXT (s7496)
HYPOTHESIS-ID: m3-partition-over-live-block

Work unit: class EU. ES/ET (s7494/s7495) showed the game re-partitions fixed RAM per display mode: the DL-chunk pool
[0x720000, end) (end 0x777768 / 0x738F18 / 0x792780 for 320 / 640x480 / 640x340) and the mode's Z/colour images, laid over heap
blocks it freed shortly before (port == retail). Open question: is EVERY rs_malloc block under a new partition already freed, in every
scene (boot, hangar, mission load, abort/re-entry), on dd1 AND dd>1 (spill arena / OSMEM 12 change the heap top)?
Hypotheses: H-eu-clean (0 live blocks under any partition; retail design holds) / H-eu-live (a live block sits under the pool or an
image extent: name the block's allocator ra and whether retail does the same via the oracle) / H-eu-dd (only dd>1 arms overlap: our
heap-top / spill change moved a live block under a retail partition = port defect, fix it).
Instrument, ONE build: export from src/main/upstream_compat.cpp a query `rs64_s7475_live_overlap(lo, hi, cb)` over s_s7475_live
(needs ROGUESQ_S7475_CANARY=1); call it from rs64_s7495_pool (pool extent) and from rs64_s7495_img for each NEW colour image
(extent = addr .. addr + w*rows*siz, rows 480 cap) and depth image (w = last colour width, 2 B/px). Log `[s7495] live-under kind=
pool|cimg|zimg blk= req= ra= age=` (first 20) + counts in `[s7495] sum`. Positive control (same run): ROGUESQ_S7495_CTL=1 records a
fake live block at 0x80787810 size 0x6C30 just before pool #3 -> MUST log live-under kind=pool blk=80787810.
Run: L4 dd1 and L15 dd8 21:9 via the s7493 recipe (`env LV="4:1:os_rt64fb 15:8:os_rt64fb" WBWATCH=787830 zsh tools/s7493_er_recipe.zsh`,
add ROGUESQ_S7495_POOL=1 to its C string) + a hangar abort/re-entry arm (s7483 route). Outcomes: 0 live-under with control caught ->
H-eu-clean, close EU; rows only at dd>1 -> H-eu-dd; rows in dd1 too -> oracle-check that block (tools/s7494_es_oracle.zsh lo hi secs).
