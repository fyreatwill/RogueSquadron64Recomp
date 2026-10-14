# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4867: loop bound is 3 in both (refuted). Retail 703 entries:703 builds:702 stores, branch 0x80091390 always taken. Port has ~2 synth entries per store; the extra one takes FALL (ring byte 0x801496F0 advanced), counter 0, no store.
Hypotheses: (H-A) the port runs runAiAudioStreamPlaybackLoop's producer write 0x8008EE6C twice per synth entry, retail once; (H-B) producer writes match but the port invokes synth twice per frame (second host/guest trigger); (H-C) timing only (port audio frames shorter).
Discriminator: retail oracle --watch-pc 0x8008EE6C,0x8008EE04,0x8009123C (control whole-RDRAM) vs port count of 0x8008EE6C (add kind to tools/apply_s4869_join.py style helper) over the same hangar window. Equal producer:entry ratio 1:1 in retail and 2:1 in port -> H-A; 1:1 in both -> H-B (then log thread id/sp at each entry). Also record why retail TAKEN builds see 1.9 incrs.
Do not retry ra logging (r31 = 0 in the port).
