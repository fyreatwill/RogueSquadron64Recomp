# Next work unit (s4438): why does SDL title audio queue starve if submit cadence matches retail?

HYPOTHESIS-ID: m5-sdl-consume-rate

s4437 result: retail title submits ~1.15 x 768 B buffers per VI swap, same cadence as the port (~59/s). So starvation is host-side. Re-derive the "115 buffers/s needed" figure: dac rate x bytes/frame / 768 vs actual AI DMA length per submit; check whether the port's SDL spec freq matches the game's programmed AI dacrate (reapplyAudioConfig) and whether the port resamples/drops. Discriminate: (a) SDL freq != game freq, (b) AI length per submit is half what retail uses, (c) queue underrun from late-submit. Positive control: log queue bytes and SDL callback consumption over the same title window.
Tool notes: build with `clang` (not cc); no `$?`/`timeout` compounds.
