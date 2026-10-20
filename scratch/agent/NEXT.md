# NEXT: name the writer that reverts forced B40 (3/5 -> 2) in G1 level select
Context (s5702): s5701 soaks had a working watch (7 hits) but the hit command list kept only `continue` (lldb multi -o quirk) - no bt. Fixed to multi-line `command add 2`..`DONE`; queued s5702_wpb40_a (force3) / _b (force5).
Hypotheses: H1 bulk copy/DMA/bzero over 0x80130Bxx; H2 halfword/word store aliasing B40; H3 save record reloaded pristine (rec[5]=2) and re-applied; H4 watch too late/miss.
Discriminator: read scratch/agent/m6/s5702_*/lldb_att1.log. FIRST check `watchpoint list` shows bt/memory read/expression in the command list and that bt frames appear per hit (positive control). Then the hit with val=3 followed by hit with val=2 names the reverter by frame. If no val=2 hit, writer is host-side (memcpy in C) -> grep src for 0x130B.
Then: patch the source of the 2 (e.g. save-record reload) so forced N survives; run force3 mission to see lv3 init.
HYPOTHESIS-ID: g1-level-select
