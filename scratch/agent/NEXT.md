# Next work unit: bisect the early fillSampleStreamRange crash (s4277)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4276: s1949 recipe crashes 5/5 at ~16-20 s in fillSampleStreamRange+9264 (<- musyxRenderVoiceSamples <- musyxMixActiveVoices, last-guest-pc 0x8000834c), env S4271/S4272 irrelevant.
Hypotheses: H1 a default turned on since s1950 (KEEP_PIPE, private-DMEM, audio defaults) moves the crash earlier; H2 a source commit after s1950 regressed voice state; H3 the dropped log flags / M4_Y8000 change timing.
Discriminator: grep the crash log for the faulting address/register (what deref), then run s1949 recipe verbatim vs with each recent default env-disabled (list via git log -30 --stat for default flips); count runs reaching [phase] 512 (need 2/3). Then resume scratch/agent/s4275_ab.sh.
