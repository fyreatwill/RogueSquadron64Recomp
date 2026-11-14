# NEXT (s7324): class G, RCP-visible references to spill blocks
HYPOTHESIS-ID: spill-rcp-ref
Context: s7317-s7323 closed classes A-F (spill pointer as a CPU value: top byte, order, difference, truncation, re-tag, index). The
spill arena 0x81000000-0x813FFFFF is PHYSICAL 0x01000000-0x013FFFFF, above the 24-bit SP DRAM_ADDR and DL segment-address range.
If any of the 42 spill owner types (scratch/s7317/d8_owner_table.txt) is read by the RSP (vertex / matrix / texture / DL chunk /
audio sample) its DMA either carries bits 24+ (hardware drops them -> reads heap at phys 0x00xxxxxx) or the game masked the pointer
to 24 bits first (class D found no such site at runtime). Either way the RCP would draw/play garbage, a plausible source of dd>1-only
terrain drops (G5b). HEAP-ADDR-AUDIT line 13 says "spill blocks are not on those chains" by design: never measured at dd8.
Hypotheses: H-cpu-only (no RCP DMA / DL address ever falls in spill or its 24-bit alias of a live spill block) vs H-rcp (some do:
name the owner type and the DMA/command, then move that allocation class below 16 MB or out of the spill path).
Unit (ONE build, ONE run):
1. Read src/rsp/s7094_dma_shape.cpp (ROGUESQ_S7094_DMASHAPE=1, =ctl control) and the DPC bridge DL walk. Add to the s7094 census:
   per RSP DMA, raw dram address before any mask; flag phys >= 0x01000000 (spill direct) and, with ROGUESQ_S7317_ALLOCMAP=1, phys
   whose 0x80000000|addr or 0x81000000|(addr&0xFFFFFF) is inside a LIVE spill block (alias); keep first 8 examples with task type
   (gfx/audio) and the DMEM target. Positive control: =ctl injects one DMA from a live spill block address per second (must count).
2. CPU side in the same build: at osSpTaskStart / task submit, walk the gfx DL (F5 table, docs/F5-UCODE-REFERENCE.md) and the audio
   command list for address words; count addresses that resolve (segment table) into spill.
3. Run dd8 21:9 L4 flight ~200 s (recipe as s7321 probe run). Outcomes: 0 hits with control fired -> class G closed, spill audit
   family A-G done; any hit -> owner type + command, fix (allocate that class from the heap / below 16 MB), two-arm qualify.
