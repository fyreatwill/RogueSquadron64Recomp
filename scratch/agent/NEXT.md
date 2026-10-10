# NEXT: which structure still points into the freed 47664-byte node block (0x8017D910..0x188000) after the 3rd audio init in the port?

HYPOTHESIS-ID: musyx-stale-stream-node-after-teardown

Context: PORTING-STATE s4526. Retail and port both relocate the node pool 0x8017D2A0 -> 0x801F9CE0 at ~6.5 s and both free the 0x8017D910 block first; retail's active list (0x801499B4) holds only 0x801F9xxx nodes in 10-55 s. The port's later crash batch (~122 s after VI 1024) reads a node at 0x17DBE0 (links 0x8017DD10/DCF8) inside the freed block.
Hypotheses: (A) a list link (0x1499B4 chain / 0x1499E4 recycle list / prev-next of a 0x801F9xxx node) is left pointing into the old block by a port-only path; (B) a voice-array entry (base *(0x801496F8), count lhu 0x80149700) keeps the old block pointer and retail would too but its voices are reaped; (C) retail does the same late and the oracle has not reached the mission phase.
Discriminating measurement (one build, one port run): extend the s4231-P poller in src/main/upstream_compat.cpp (~line 1452) to walk the 0x1499B4 and 0x1499E4 chains (bounded <=2100 steps) every poll and log the FIRST time any node address or link falls in 0x8017D000..0x80188000, with last guest pc and the holder address; also scan the voice array for words in that range. Positive control: log chain length (must be >0, ~20-40 nodes in 10-40 s).
Outcomes: A => holder address names the writer (store-watch it); B => voice field offset names it; neither => C, enqueue as a soak (base on s4300_rsfreebt.sh) and move on.
