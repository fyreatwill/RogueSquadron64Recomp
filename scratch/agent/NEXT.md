# Next work unit: who leaves allocator head (0x8014999C-ish: lui 0x8015 -0x661C) and pool (-0x6634) == 0 with tail nonzero, and why ra==0 at fillSampleStreamRange

HYPOTHESIS-ID: m5-audio-destub-sequence

s4233: +8292 is the unlink at 0x8008FD60 with v1==0 (head=0 pool=0 tail=801F9E00 ra=0, seen once in r1). +932 is the walk at 0x8008FADC with t0=0x10CF3001.
Hypotheses: (a) fillSampleStreamRange runs before the allocator init (ra=0 means a thread/entry started with zeroed ctx, so the callee runs uninitialised); (b) a guest memset/clear zeroes head+pool but not tail; (c) save/stale-state dependent.
Discriminator (one build, one run set): in fillSampleStreamRange entry, print head/pool/tail/ra with a global call ordinal, plus the ordinal of the allocator init store (watch writer of head with PC) — a positive control is the same print in a surviving run (head!=0). Outcome (a): first call ordinal precedes init store; (b): init store precedes, and a later zero store with PC appears; (c): differs between fresh and stale save.
Use scratch/agent/s4230_listwatch.sh pattern; read host pc-symbol via `cmake --build ... --target ...funcs_N.s` + scratch/agent/s4233/map.py.
