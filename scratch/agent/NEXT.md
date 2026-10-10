# NEXT: why does musyxSynthFrame still walk stream nodes after audio teardown?

HYPOTHESIS-ID: musyx-stale-stream-node-after-teardown

Evidence: s4522 4/4 arms hit the do_rom_read odd-address assertion ~122 s after VI 1024 (RSP fix irrelevant). s4299: node block (~0x17D000..0x17E200) freed by audio teardown, reallocated to loadLevelTextureCache, synth frame still walks it.
Hypotheses: (A) teardown never unlinks nodes from the synth-frame list because an audio stub/gate skips the unlink (M5 de-stub target); (B) retail walks the same list but its allocator does not reuse the block in that window; (C) a gated path resets the list head.
Work unit: grep-enumerate writers/readers of the stream-node list head used by musyxSynthFrame and the teardown function that frees the block (free site from s4299); list every stub/gate on that path in docs/M5-AUDIO-PLAN.md. A gate skipping an unlink => A; no gate => B/C, then oracle-watch the list head in retail.
