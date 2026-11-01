# NEXT: G1e — cut the LLE interpreter's per-RDP-command cost so dense lvl5 dd4 FPS60 tasks drop below ~14 ms
HYPOTHESIS-ID: g1e-rsp-segment

s6712 ([g1e-split], ROGUESQ_G1E_AQ=1; `sample` + tools/sample_gfx_split.py, tools/sample_self.py): gfx task = ~0.6 ms + 257 ns per RDP command
(interp side) + 55 ns/cmd bridge (half is the timer). Dense camera phase 35-50k cmds -> 12-16.6 ms. Profile (owner config,
y8000 fixed): interpreter ~70% (factor5_ucode self, RSP::VMADN/VMADH/SDV/VMADM/VMUDL out-of-line templates, byte-wise
dma_rdram_to_dmem ~7%), bridge ~10%, unconditional in-ucode probes ~10% (rs64_dlw_jump, rs64_s4209_read,
rs64_inline_probe_route, rs64_g1d_blk_dma, rs64_probe_audio_dma_write, census chain, floor_writer, e9prov_ovl_route).

## Hypotheses (which lever buys the ~15-20% needed)
- H-probes: the ~20 unconditional probe calls per DMA / per ucode site; gate them behind rs64_rsp_hooks_on (check each
  probe's env list is in the rs64_rsp_hooks_on on-list first, or the gate silently disarms an instrument).
- H-dma: byte-wise MEM_B/RSP_MEM_B loops in rsp.hpp dma_* (lib/: export.sh + commit) -> word-wise swizzled copy.
- H-vops: RSP:: vector templates not inlined into factor5_ucode (check -O2 actually applies to build/factor5_ucode; try
  always_inline / -O3 for that target).

## Work unit (ONE build, same-run toggle)
1. Implement H-probes + H-dma behind a runtime global (ROGUESQ_G1E_FAST_TOGGLE=<sec> flips it like STORE_DIAG_TOGGLE).
2. Run `zsh scratch/agent/s6712_owner.zsh 5 4 fast` (owner config + G1E_AQ) with the toggle env added; compare rest ns/cmd
   per window (fit as in s6712: rest = a + b*calls). Positive control: the toggle window boundary [g1e-split] lines.
3. If H-vops remains the bulk, check compile flags of the factor5_ucode target (ROGUESQ_SRC_OPT) next.
Outcomes: slope drop >=15% -> qualify lvl1/5/10 300 s (fb sane) and measure tasks/s; <5% -> H-vops is the lever.
