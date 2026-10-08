# Next work unit (s4291): arm1 alone to hangar VI 512

HYPOTHESIS-ID: m5-audio-destub-sequence

s4290: concurrent two-arm route puts title at ~52 s and never reaches 512; restore effect (odd 58-60 vs 0) reproduced at VI 640/title.
Hypotheses: Q1) restore removes hangar garbage fb-set growth; Q2) another writer; Q3) WRAP_FLUSH+shadow cost hurts.
Discriminator: run scratch/agent/s4290_hangar_ab.sh with only arm 1 (edit loop to `for arm in 1`), then arm 0 sequentially (1024 phase -> keys 2/6/10/14 -> wait for 512; check probe.sh duration arg semantics first). Control: arm0 odd>0.
