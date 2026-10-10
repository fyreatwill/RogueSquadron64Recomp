# NEXT: what gates the port synth's stream-node walk during 640 attract that retail's does not?

HYPOTHESIS-ID: musyx-stale-stream-node-after-teardown

Context: PORTING-STATE s4525. Retail overlays 0x17D004..0x17E1E0 at 9.5 s yet submits 0/2007 text DMA entries 10-55 s; node rebuild (0x8008FBB4) only from 38.7 s. Port walks nodes in the same window.
Hypotheses: (A) retail's node list head (read in musyxSynthFrame) is 0/empty at 640 so no node DMAs; port head non-zero (some init the port runs or skips). (B) retail walks the same nodes but entries >4 of batch or the DMA size/ordering hide it (check entries 5+). (C) retail frees the list head's owner earlier and the list is relinked.
Discriminating work unit: find the head-pointer load in musyxSynthFrame (grep funcs for the node walk, read via 0x8009123C region / s4298 notes), oracle --watch-pc on the load with RS64_ORACLE_A0WORDS and a read watch of the head word at 10-38 s: head value + node count retail vs port (port ROGUESQ log equivalent). Also dump entries beyond 4 by raising A0WORDS to 30 and rescanning (cheap, same script: scratch/agent/s4525_oracle_dma.sh).
Outcomes: head empty in retail => chase the port writer that populates it (M5 de-stub step). Entries 5+ show text => A/B reversed, retail also issues them.
