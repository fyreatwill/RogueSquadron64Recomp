# NEXT (s7338): idiom-class audit - class M, physical 8 MB masks in host code
HYPOTHESIS-ID: phys-8mb-masks
Context: s7337 closed class R (guest-range 0x80800000 bounds; tools/s7337_bound_census.py). Its census counts 193 physical-address
literals in host code that assume 8 MB RDRAM: `& 0x7FFFFF`, `& 0x7FFFFC`, `< 0x800000`, `0x800000 - x`. At dd>1 guest data lives up
to 0x80C00000 and host arenas (DLPOOLX 0x80C00000.., spill 0x81000000..0x81800000) are read by the gfx path, so a live-path mask would
fold 0x80C01234 onto 0x00401234 (silent wrong read) or reject it.
Sites: `python3 tools/s7337_bound_census.py` prints the count; enumerate with the MASK regex in that tool over src/main/*.cpp,
src/rsp/dpc_bridge.cpp, src/main/rt64_render_context.cpp, lib/N64ModernRuntime/{ultramodern,librecomp}/src/*.cpp. Already seen:
factor5_gfx_runner (DL walkers 7335-7558, sh2 shadow 6710), rs64_run_lle_gfx (LOG_SEQ dump), rt64 map_result (texture dump),
dpc_bridge e9prov/f5 shadow (logging), sp.cpp dump_frame, events.cpp ramsnap, upstream_compat rs64_g1d_blk_dma.
Hypotheses: H-diag (every live-path mask sits behind an env/log gate), H-alias (a default-on path masks a >8 MB address: look first at
the DL walkers in factor5_gfx_runner and anything in dpc_bridge submit/defer/wrap, RSP DMA, ai.cpp), H-intended (24-bit RSP
segment math where 0xFFFFFF would be right and 0x7FFFFF is a typo-class bug only above 8 MB).
Method: extend the census with class M: classify every mask site by enclosing function gate (D/A/X as in s7337), list default-on ones.
For any H-alias site: switch to 0xFFFFFF / rs64_ram_top behind ROGUESQ_S7338=0, with a counter of addresses >= 0x800000 seen there
(positive control: counter > 0 in a dd8 21:9 L1 arm via scratch/s7337/run.zsh, 0 at dd1).
