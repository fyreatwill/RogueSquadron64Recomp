# Next work unit (s4457): characterise musyxSynthFrame+5436 crash with ROGUESQ_AI_EVENT_HZ=115 (reproduces ~15 s)

HYPOTHESIS-ID: m5-ai-event-cadence

s4456: hz115 3/4 crash at ~15 s at musyxSynthFrame+5436 vs ctl 0/4 early. Mix rate matches retail, so the defect is real state exposed by mix calls.
Work: with hz115 armed, dump at crash: faulting address/regs, voice index, voice struct fields; name the WRITER (ORIGIN line). Hypotheses: (A) voice array uninit/stale entry from missing audio init; (B) bad DMA'd sample/adpcm state pointer; (C) a stubbed MusyX callback leaves a field 0. Discriminator: faulting field value pattern (null / stale ptr / ROM addr).
Note: no `timeout` binary; concurrent arms only.
