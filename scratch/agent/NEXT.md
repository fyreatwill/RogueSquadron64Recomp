# NEXT (s5688): bool 7 / voice-script path vs mission failure (G1, Next steps #2)
Hypotheses: H1 sayWhoaHim_v0x1FC (voice path) sets objective bool 7 in failing runs only; H2 bool 7 set by non-voice path (damage/timer); H3 unrelated to voice.
Discriminator: one build logging entry to sayWhoaHim_v0x1FC + every write to bool 7 with caller PC, positive control = mark-all-bool-writes fires; compare failing vs surviving mission arms in ONE soak pair.
G2 is closed pending owner listen: see docs/G2-AUDIO-FIDELITY-CLOSURE.md.
HYPOTHESIS-ID: g1-bool7-voice-path
