# Next work unit
HYPOTHESIS-ID: retail-entry-revisit
s4978 result: retail flagged voices always have voice+0x6D==3; the +0x6D==0 branch (0x80090358 -> 0x800903F0) is never taken (0/241,308). The port takes it with ASCII in voice+0x34.
Work unit: ONE port build/run with a phase-gated histogram of lbu 0x6D(s1) and lhu 2(s1) at 0x800901C8, plus attribution of every store PC that writes a voice record's +0x6D byte (voice base 0x801724C0, find stride from musyxInitVoiceFromSample). Positive control: count at 0x800901C8 > 0.
Hypotheses: H1 port voices never initialised with kind=3 (init path skipped/stubbed, an M5 audio artifact); H2 kind byte overwritten by a stray store of ASCII data; H3 slot index out of range, reading a neighbouring non-voice record.
Discriminator: histogram of +0x6D values and writer PCs. Retail comparison: oracle watch-write on a voice +0x6D byte for writer PCs.
