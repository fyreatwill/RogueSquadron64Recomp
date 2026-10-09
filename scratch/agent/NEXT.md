# Next work unit (s4449): does retail ever EXECUTE musyxRenderVoiceSamples (0x8008FFAC)?

HYPOTHESIS-ID: m5-ai-event-cadence

Known (s4448): retail 20s boot/title: 0 reads of voice0 0x1951B8..+0x88 (control 2.83M reads). Single-source until exec confirmed.
Hypotheses: (b) retail never enters 0x8008FFAC in title -> port caller gate is the defect; (c) retail enters but voice array lives elsewhere.
Discriminator: tools/oracle --watch-pc 0x8008FFAC (and 0x80035500 osViSwapBuffer as positive control) 20s. Hits>0 => (c): find voice base from $-regs; 0 => (b): find port caller of musyxRenderVoiceSamples and what retail gate it bypasses.
