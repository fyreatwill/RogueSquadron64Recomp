# Next work unit (s4302): in retail, does anything read the freed stream-node block after waitForAnyAudioSlot's three frees?

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4301): the free is verbatim retail code in waitForAnyAudioSlot (frees ptrs at 0x80139B4C/B50/B54 when byte 0x80130B39==0), taken on the natural first-poll exit; guard/yield not involved (control cap=1 fires, default 0). pc 0x80095D54 was a stale last-guest-pc.
Hypotheses:
- H-retail-same-walk: retail also frees and the synth keeps walking, but retail's reuse of the block differs (texture cache allocates elsewhere), so no corruption.
- H-flag-differs: retail has byte 0x80130B39 != 0 (frees skipped) at this point and ours is 0 because of an upstream audio stub.
- H-order: retail stops the synth earlier (e.g. 0x80130B39 or a synth-enable flag set by code we skip).
Discriminator: tools/oracle (README) — read-watch physical 0x00130B39 and write-watch 0x00139B4C..B54 (positive control: whole-RDRAM watch fires), on retail reaching the mission transition; log value of 0x80130B39 at the waitForAnyAudioSlot return and who writes it. Compare to ours (log byte at the same point). Note the oracle reaches only boot/attract; if the transition is unreachable, instead log our writer of 0x80130B39 (rs64_m5_writer_parity) and its value history.
