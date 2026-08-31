# M5 Session 3431 — reapplyAudioConfig producer boundary

The port witness sampled reapply entry, the post-`osAiSetFrequency` point,
and the pre-mixer argument formation in one build. In title,
`osAiSetFrequency` returned `0x5622`; mixer entry received `a1=0x0F`, then
`0x8009192C` reloaded `a1=0x5622` for `allocateSongChannelArray`. In hangar,
the same path returned `0x5622` and passed `a1=0x12`.

The independent retail oracle passed its whole-RDRAM control at 10,000
writes. Physical `0x165ED0` had 5,643 writes, including 1,125 in title
1024; post-value sampling saw 32 nonzero values. The broad title writer
histogram included `0x800331E0` once, but did not isolate the exact frequency
return edge. Its PC watches were armed after the relevant phase and are
unevaluable, not negative evidence.

This selects `H-PortFrequencyResultProducer` for the observed port flow and
refutes a direct setup-caller argument as the source of `0x5622`. It does not
establish whether the port result is legitimate or why the retail result
differs. No runtime behavior was changed.

Evidence: `scratch/agent/s3431_m5_reapply_boundary/`,
`scratch/agent/s3431_m5_oracle4/oracle.log`, and
`scratch/agent/s3431_m5_oracle5/oracle.log`.
