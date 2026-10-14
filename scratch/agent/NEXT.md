# Next work unit (M5 task data_size writer)

HYPOTHESIS-ID: m5-task-family-retail-compare

s4862: retail OSTask(0x80149470) data_size is 2 in ~90% of rows (title 572/625, hangar 188/210); port (s4860) is 1-dominant. Reproducible, same slots.

Hypotheses: (a) timing only: port queues fewer audio frames per swap; (b) guest-side frame-count writer behaves differently in the port.
WORK UNIT: oracle exact-memory write watch on phys(0x80149470+0x24) (data_size field; verify offset in tools/oracle README/OSTask layout) with whole-RDRAM control, title phase, to name writer PCs; then port-side same-field writer rows in one phase-gated run (reuse s4860 harness). Discriminator: same writer PC and a value derived from a different count => (b); same writer with values tracking per-swap producer cadence => (a).
