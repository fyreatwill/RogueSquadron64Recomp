# Next work unit: is the hangar's repeated all-nonzero AI buffer (FNV 0x95E590C5) real audio or a constant/saturated fill?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4235: fresh-save hangar run (scratch/agent/s4235_hangar_pcm.sh, hangar at 72 s) gave 19/25 identical AI buffers, nz=768/768.
Hypotheses: (a) constant DC/clipped fill (mixer saturating or an uninitialised bus); (b) legitimate looping ambience/music tail repeated; (c) host-side repeat of a stale buffer.
Discriminator: at the ai.cpp `[ai-output]` census also log the first 32 bytes and per-channel s16 min/max/distinct-count of each buffer. (a) -> min==max or 1-2 distinct values; (b) -> wide distinct count, different FNVs on later buffers; (c) -> same rdram addr reused. Positive control: title buffers in the same run must show wide distinct counts.
Optional retail twin: tools/oracle/README.md hangar AI buffer (oracle currently reaches boot/attract only, so likely unavailable).
Park: allocator head==0/tail!=0 corruption (s4234) until it recurs.
