# Next work unit: read s5483_postloop (scratch/agent/m6/s5483_postloop/lldb_att1.log, SOAK-RESULTS.md)
Question: after flags|=0x40 (t~848 in prior run), does runInMissionFrame hit bufferArbiterProducerScanWait and return to mainGameLoop? What does mainGameLoop call next (initMission/loadOverlay breakpoints)?
Hypotheses: (A) loop returns, mainGameLoop re-enters a results/overlay path that renders the 0x720000/0x790000 presents -> read that path. (B) breakpoint never hit after 0x40: loop still running (another exit condition at loop head L_800FA728 or flag cleared) -> find the clearing writer with a wp on 0x10CA1C. (C) loop returns but mainGameLoop re-enters runInMissionFrame immediately (restart of same mission) -> see runInMissionFrame bp hits post-0x40.
Discriminator: order of bp hits after the 0x40 write in lldb_att1.log (bt 3 frames).
Control: 0->4->6 and 0x40 writes must reappear.
HYPOTHESIS-ID: m6-mission-end-trigger
