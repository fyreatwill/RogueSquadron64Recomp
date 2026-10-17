# M4 generated-PC -> retail IMEM-PC mapping (s5353, offline)

Result: the mapping is exact: `retail_pc = port_pc & 0xFFF` (port_pc = 0x1000 | imem_pc).
Port `0x112C` -> retail `0x012C`; port `0x17F0` -> retail `0x07F0`.

Evidence:
1. Generator: every generated dispatcher is `switch ((jump_target | 0x1000) & 0X1FFF)`
   (tools/fixup_factor5_ucode.py:652,1081,2820) and labels are named `L_<0x1000|imem>`
   (`L_112C`, `L_17F0` in build/factor5_ucode/*_recompiled.c). tools/disasm_rsp_ucode.py and
   docs/F5-UCODE-REFERENCE.md use the same 0x1000-based RSP addresses ("IMEM 0x1024"), while
   cxd4's 12-bit PC is the bare IMEM offset.
2. Image (weak control): build/imem_dma_dump.bin (11,880 B, concatenated overlay DMAs) contains the
   ovl12 `L_112C` word `lw $8,8($18)` (0x8E480008) and `L_17F0` word `lhu $6,0x24($13)` (0x95A60024)
   at in-dump offsets 0x1130 / 0x17F4. The dump is a multi-segment concatenation, so this only shows
   the opcodes exist near those offsets; treat as single-source.

Caveats that matter more than the arithmetic:
- Port PCs are label-hook EVENTS; retail PCs are periodic SAMPLES (cxd4 RSM1, stride configurable).
  Retail min/max 0x0088/0x0FE8 are both multiples of 8; 0x12C is not, so a stride-8 sampler cannot
  see 0x12C. A join needs retail stride 1 filtered to {0x012C, 0x07F0}.
- L_112C / L_17F0 exist in many overlay variants (ovl10/12/14/1c/20/b) with different bodies; the
  key must include overlay/task type.
- Origins 0x006AB800 vs 0x006AB400 are unaligned; join by VI phase ordinal, not address.
- Not run: no retail PC histogram was available offline to confirm 0x12C / 0x7F0 occur.
