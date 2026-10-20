# NEXT: name the writer that reverts forced B40 (3/5 -> 2) in G1 level select
Context (s5700): force3/force5 soaks show saveslot writes N to B40, yet cineBody#2 sees B40=2 and lvinit gets level 2. No logged sb did it.
Hypotheses: H1 bulk copy/DMA/bzero over 0x80130Bxx; H2 halfword/word store aliasing B40; H3 save record reloaded pristine (rec[5]=2) and re-applied; H4 lldb watch too late/miss.
Discriminator: soaks s5700_wpb40_a/b (m6_wp_b40.sh). Read scratch/agent/m6/s5700_*/lldb_att*.log: control 0x3470 must hit first; then the 0x130B40 hits' bt + r31. val=3 then val=2 hit names the reverter. If no second hit, writer is host-side (memcpy in C) -> grep src for 0x130B.
Then: fix by patching the source of the 2 (e.g. save-record reload) so forced N survives, and run force3 mission to see lv3 init.
HYPOTHESIS-ID: g1-level-select
