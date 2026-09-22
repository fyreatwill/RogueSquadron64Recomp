# M5 s3695 — audio-pump route boundary

The independent retail control passed before the port run: a whole-RDRAM
watch produced 10,000 positive-control callbacks, the retail run reached the
hangar (`512`, origin `0x006AB400`), and the phase-gated source-range writer
census recorded `0x800078EC` (384 rows), `0x80007670` (172 rows), and the
`0x8001F...` family.

The existing qualified port binary was launched with real audio, ungated LLE,
LLE solo, spin yield, autopilot, and the M5 source/input diagnostics. It
remained at the initial 320 VI for 35 seconds. Neither the
`[m5-rsp-source-hook-control]` positive control nor the target
`[m5-dmem-source-control]` and `[m5-source-range-writer]` controls emitted a
row; no 1024 or 512 phase was reached.

This makes the DMEM predecessor table unevaluable for this run. It selects no
DMEM producer hypothesis and does not distinguish a zero DMEM producer, a
join mismatch, or a retail-only source path. The next boundary is the
audio-pump route that prevents the qualified real-audio arm from reaching the
target phase. No mitigation was added.
