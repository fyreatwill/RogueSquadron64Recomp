# NEXT: G1d step 23 - who fills the 1356-chunk DL pool at 8 MB and why not at 12 MB?
HYPOTHESIS-ID: g1d-widescreen
Known (s6130): RT64 caps lifted to 16 MB. OSMEM=12 (any aspect) boots with *(0x801163B0) len=0 -> beginFrameDLChunk null deref. OSMEM=8: len=1356.
Hypotheses: H-mode (game branches on osMemSize==8MB/4MB and skips pool build at other sizes), H-region (pool carved from a region whose bounds derive from the top-of-memory and lands unmapped/zero), H-order (pool built after a check on heap size that fails).
Discriminator: log first non-zero store to 0x801163B0 (hook the recwatch or add an lldb watchpoint on the guest address; positive control = 8 MB run must show it) and print the caller guest pc; then read that function's osMemSize/0x80000318 uses.
Fallback route if mode-gated and unpatchable: keep 8 MB and shrink the widened carve (depth/aux fbs at 512 wide) in partitionFramebufferMemory via fixup script.
Recipe: env TAG_SUFFIX=x XENV_EXTRA="ROGUESQ_OSMEM_MB=12 ROGUESQ_DLPOOLLOG=1 " HOLD_S=15 LEVEL=1 zsh scratch/agent/g1_level_coverage_common.zsh
