# NEXT (s7339): idiom-class audit - class N, 16 MB physical masks (`& 0xFFFFFF`) in host code vs the spill arena
HYPOTHESIS-ID: phys-16mb-masks
Context: s7338 closed class M (8 MB masks, tools/s7338_mask_census.py, B 0). The spill arena sits at 0x81000000-0x81800000 = phys
0x01000000+ (s7326), above 16 MB. Any host CPU-side read that does `rdram + (a & 0xFFFFFF)` on a spill pointer folds it onto phys
0x00xxxxxx (heap/static): silent wrong read/write. The RCP side is already closed (s7324/s7327 class G: rs64_s7327_mask widens RSP
DMA to 0x1FFFFF8 when the spill arena is live). This audit is the host CPU side.
Count: ~380 `& 0x0*FFFFFx` sites: main.cpp 120, upstream_compat.cpp 108, dpc_bridge.cpp 33, rt64 hle/rt64_rdp.cpp 25,
rt64_render_context.cpp 18, rt64_state.cpp 16, librecomp rsp.cpp 15, rt64_interpreter 8, s2dex 7, s7324_rcp_spill 5, present_queue 5.
Hypotheses: H-diag (every live mask is gated/log-only, as class M), H-fold (a default-on host path masks a spill pointer with
0xFFFFFF: look first at upstream_compat.cpp, librecomp rsp.cpp, and rt64 hle rt64_rdp.cpp/rt64_state.cpp RDRAM fetches - but the
RDP only ever sees <16 MB addresses by s7324, so rt64 masks are likely H-hw = hardware-faithful 24-bit), H-hw (masks that model
the 24-bit RDP/VI address bus: correct by design).
Method: copy tools/s7338_mask_census.py's classifier with a class-N regex (`&\s*0x0*FFFFF[0-9A-F]`), add H (hardware-bus) class for
RDP/VI register/command field decode, hand-review the rest. For any H-fold site: switch to 0x1FFFFFFF/rs64_ram_top behind
ROGUESQ_S7339=0 with a counter of phys >= 0x1000000 seen there (positive control: counter > 0 at dd8 21:9 L4 hangar route where
spill blocks are live, scratch/s7334/run.zsh recipe; 0 at dd1).
