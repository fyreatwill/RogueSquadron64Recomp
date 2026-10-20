# NEXT: static caller census of sayWhoaHim_v0x1FC (and what reads bool 7 in the 0x64 fail arm)
Hypotheses: H1 a script/voice table entry (data, not a direct call) invokes sayWhoaHim and the port never dispatches that table row (voice path gated); H2 retail also never sets bool 7 on this route, fail arm reading it is legitimate; H3 caller exists but is behind an audio/voice gate we stub. Discriminator: grep RecompiledFuncs for sayWhoaHim address refs (jal + data-table words in ROM), classify callers, then check reachability in port with one entry log.
HYPOTHESIS-ID: g1-bool7-voice-path
